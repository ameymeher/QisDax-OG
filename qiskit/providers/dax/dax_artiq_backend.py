from qiskit.providers.dax.dax_backend import DAXBaseBackend
from qiskit.providers.dax.dax_artiq_job import DAXArtiqJob



class DAXArtiq(DAXBaseBackend):
    def __init__(self, provider):
        super().__init__(provider, 'dax_artiq_device')

    def get_job_type(self):
        return DAXArtiqJob
