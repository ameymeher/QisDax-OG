from argparse import Namespace
from functools import partial
from os import getcwd, path
from tempfile import gettempdir
from dateutil.parser import parse as parse_date
import logging
import time
from artiq.frontend.artiq_client import get_argparser
from artiq.tools import parse_arguments
from paramiko import AutoAddPolicy, SFTPClient, SSHClient
from qiskit.providers.dax.dax_job import DAXJob
from sipyco.pc_rpc import Client
from h5_artiq.reader import H5Reader

from qiskit.providers.dax.config import get_config

def action_submit(remote: Client, args: Namespace):
    """cloned [_action_submit](https://github.com/m-labs/artiq/blob/b50d30ba5bcf218342db545fac68685eb6ba1c7b/artiq/frontend/artiq_client.py#L129)"""
    try:
        arguments = parse_arguments(args.arguments)
    except Exception as err:
        raise ValueError("Failed to parse run arguments") from err

    expid = {
        "log_level": logging.WARNING + args.quiet*10 - args.verbose*10,
        "file": args.file,
        "class_name": args.class_name,
        "arguments": arguments,
    }
    if args.repository:
        expid["repo_rev"] = args.revision
    if args.timed is None:
        due_date = None
    else:
        due_date = time.mktime(parse_date(args.timed).timetuple())
    rid = remote.submit(args.pipeline, expid,
                        args.priority, due_date, args.flush)
    return rid


class DAXArtiqJob(DAXJob):
    
    def get_raw_data(self, fname):
        h5 = self.run_artiq(fname)
        reader = H5Reader(h5)
        ds = reader.get_datasets()
        return ds["histogram_context"]["histogram"]["raw"][0]
    
    def upload_program(self, file, remote_path, sftp):
        sftp.put(localpath=file, remotepath=remote_path)

    def retrieve_result(self, fname, result_dir, sftp:SFTPClient):
        for date_dir in sftp.listdir(result_dir):
            for subfolder in sftp.listdir(date_dir):
                for filename in sftp.listdir(subfolder):
                    if path.basename(filename) == fname:
                        localpath = path.join(gettempdir(), fname)
                        sftp.get(filename, localpath)
                        return localpath


    def sftp_util(self, callback):
        credentials = get_config(f'{getcwd()}/credentials.ini')
        ssh_section = credentials["client_ssh"]
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=ssh_section["hostname"], username=ssh_section["username"], password=ssh_section["password"], allow_agent=False)
        sftp = ssh_client.open_sftp()
        try:
            result = callback(sftp)
            return result
        finally:
            sftp.close()
            ssh_client.close()

    def run_artiq(self, file):
        parser = get_argparser()
        config = get_config()

        program_client = config["remote"]["remote_program_client"]
        args = parser.parse_args(['submit', file, program_client])

        remote_path = path.join(config["remote"]["remote_dax_dir"], path.basename(file))
        self.sftp_util(callback=partial(self.upload_program, file, remote_path))

        section_name = "submit"
        section_submit = config[section_name]
        for arg_key in section_submit:
            arg_action, = [item for item in parser._actions if item.dest == arg_key]
            setattr(args, arg_key, arg_action.type(section_submit.get(arg_key)))
        arguments = args.arguments
        arguments.append(f'file="{remote_path}"')
        section_arg_name = "submit.arguments"
        section_arguments = config[section_arg_name]
        for arg_key in section_arguments:
            arguments.append(f'{arg_key}="{section_arguments[arg_key]}"')
        port = 3251 if args.port is None else args.port
        target_name = "master_schedule"
        remote = Client(args.server, port, target_name)
        try:
            rid = action_submit(remote, args)
            fname = "{:09}-{}.h5".format(rid, path.splitext(path.basename(program_client))[0])
            time.sleep(config.getint("misc", "wait"))
            h5 = self.sftp_util(callback=partial(self.retrieve_result, fname, config["remote"]["remote_result_dir"]))
            return h5
        finally:
            remote.close_rpc()
