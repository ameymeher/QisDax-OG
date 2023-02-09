from argparse import Namespace
from dateutil.parser import parse as parse_date
import logging
import os
import time
from artiq.frontend.artiq_client import get_argparser
from artiq.tools import parse_arguments
from qiskit.providers.dax.dax_job import DAXJob
from sipyco.pc_rpc import Client

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
    print("RID: {}".format(rid))


class DAXArtiqJob(DAXJob):
    
    def get_raw_data(self, fname):
        raw = self.run_artiq(fname)
        return raw

    def run_artiq(self, file):
        parser = get_argparser()
        args = parser.parse_args(['submit', file])
        env_vars = os.environ
        env_prefix = "QISDAX_ARTIQ_"
        env_qisdax_artiq = [item for item in env_vars if item.startswith(env_prefix)]
        for env_var in env_qisdax_artiq:
            arg_key = env_var.replace(env_prefix, "").lower()
            arg_action, = [item for item in parser._actions if item.dest == arg_key]
            args[arg_key] = arg_action.type(os.environ.get(env_var))
        port = 3251 if args.port is None else args.port
        target_name = "master_schedule"
        remote = Client(args.server, port, target_name)
        try:
            action_submit(remote, args)
        finally:
            remote.close_rpc()
