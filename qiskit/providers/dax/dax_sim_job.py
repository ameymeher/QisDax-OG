from qiskit.providers.dax.dax_job import DAXJob

from dax_program_sim.frontend.dax_prog_sim import config_parser, backend_config_parser
from dax_program_sim.frontend.runtime import DaxProgramSimFrontendError, run, BACKENDS_MAP

class DAXSimJob(DAXJob):
    
    def get_raw_data(self, fname):
        raw = self.run_sim(fname)._data_context.get_raw()[0]
        return raw

    def run_sim(self, file):
        config_args = config_parser()  # Gets config arguments
        num_qubits = config_args.get('num_qubits')
        backend = config_args.get('backend')
        if num_qubits is None:
            raise DaxProgramSimFrontendError('Number of qubits not specified in config file')
        if backend not in BACKENDS_MAP:
            raise DaxProgramSimFrontendError('Backend specified in config is invalid')
        backend_configs = backend_config_parser(backend)

        arguments = {}
        # Add file and class into argument dictionary
        arguments['file'] = file

        # Get managers and enable simulation with DAX.sim. Add the arguments to the dataset manager to be picked up later
        return run(artiq_arguments=arguments, num_qubits=num_qubits, backend=backend, backend_config=backend_configs)
