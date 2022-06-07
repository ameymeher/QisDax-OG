from qiskit.providers.dax.dax_backend import DAXBaseBackend
from qiskit.providers.dax.dax_sim_job import DAXSimJob



class DAXSimulator(DAXBaseBackend):
    def __init__(self, provider):
        super().__init__(provider, 'dax_code_simulator')

    def get_job_type(self):
        return DAXSimJob