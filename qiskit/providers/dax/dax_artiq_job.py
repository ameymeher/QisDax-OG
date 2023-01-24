import os
from artiq.frontend.artiq_client import _action_submit, get_argparser
from qiskit.providers.dax.dax_job import DAXJob
from sipyco.pc_rpc import Client

class DAXArtiqJob(DAXJob):
    
    def get_raw_data(self, fname):
        raw = self.run_artiq(fname)
        return raw

    def run_artiq(self, file):
        parser = get_argparser()
        args = parser.parse_args([])
        args.file = file
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
            _action_submit(remote, args)
        finally:
            remote.close_rpc()
