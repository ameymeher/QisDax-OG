from qiskit.providers.dax.dax_backend import DAXBaseBackend
from qiskit.providers.dax.dax_print_job import DAXPrintJob



class DAXPrinter(DAXBaseBackend):
    def __init__(self, provider):
        super().__init__(provider, 'dax_code_printer')

    def get_job_type(self):
        return DAXPrintJob