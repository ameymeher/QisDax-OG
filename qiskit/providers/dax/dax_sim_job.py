from collections import Counter
import numpy as np
from qiskit.providers.dax.dax_job import DAXJob

import dax.util.artiq
import dax.sim
from dax_program_sim.backend.qiskit_aer import QiskitAer
from dax_program_sim.data_context.program_sim_data_context import ProgramSimDataContext
from dax_program_sim.frontend.dax_prog_sim import _BackendClient, _DEVICE_DB

class DAXSimJob(DAXJob):
    
    def get_raw_data(self, fname):
        raw = self.run_sim(fname)._data_context.get_raw()[0]
        return raw

    def run_sim(self, file):
        arguments = {}
        # Add file and class into argument dictionary
        arguments['file'] = file


        # Get managers and enable simulation with DAX.sim. Add the arguments to the dataset manager to be picked up later
        managers = dax.util.artiq.get_managers(
            device_db=dax.sim.enable_dax_sim(_DEVICE_DB, enable=True, output='null', moninj_service=False),
            arguments=arguments
        )

        # Use the Qiskit Aer statevector backend always
        operation_cls = QiskitAer

        try:
            # Create a composite class to combine program client and system.
            # System arguments are passed on the interior while client arguments are passed on the exterior
            exp = _BackendClient(managers, data_context_cls=ProgramSimDataContext, operation_cls=operation_cls)
            # Run each experimental stage. Runs through each part of the ProgramClient
            exp.prepare()
            exp.run()
            exp.analyze()
        finally:
            # Ensure graceful exit of core devices
            managers.close()
        return exp
