from collections import Counter
import importlib
import numpy as np
from qiskit.providers.dax.dax_job import DAXJob

import dax.util.artiq
import dax.sim
from dax_program_sim.data_context.program_sim_data_context import ProgramSimDataContext
from dax_program_sim.frontend.dax_prog_sim import config_parser, DaxProgramSimFrontendError, BACKENDS, backend_config_parser
from dax_program_sim.frontend.dax_prog_sim_run import _DEVICE_DB, BACKENDS_MAP, _BackendClient, _set_backend, get_backend

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
        if backend not in BACKENDS:
            raise DaxProgramSimFrontendError('Backend specified in config is invalid')
        backend_configs = backend_config_parser(backend)



        arguments = {}
        # Add file and class into argument dictionary
        arguments['file'] = file

        # Get managers and enable simulation with DAX.sim. Add the arguments to the dataset manager to be picked up later
        managers = dax.util.artiq.get_managers(
            device_db=dax.sim.enable_dax_sim(_DEVICE_DB, enable=True, exclude=['dps_device', 'core'], output='null',
            moninj_service=False),
            arguments=arguments
            )

        try:
            operation_mod = importlib.import_module(BACKENDS_MAP.get(backend).get('module'))
            operation_cls = getattr(operation_mod, BACKENDS_MAP.get(backend).get('class'))
        except AttributeError:
            raise DaxProgramSimFrontendError('The backend specified does not exist')

        if backend_configs is None:
            backend_configs = {}

        try:
            # Create a composite class to combine program client and system.
            # System arguments are passed on the interior while client arguments are passed on the exterior
            exp = _BackendClient(managers, data_context_cls=ProgramSimDataContext, num_qubits=num_qubits,
                                backend_args=backend_configs, operation_cls=operation_cls)
            _set_backend(exp.registry.search_interfaces(dax.interfaces.operation.OperationInterface)[exp._operation_key])
            # Run each experimental stage. Runs through each part of the ProgramClient
            exp.prepare()
            exp.run()
            get_backend().cleanup()
            exp.analyze()
        finally:
            # Ensure graceful exit of core devices
            managers.close()
        return exp
