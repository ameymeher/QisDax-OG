from qiskit.providers.dax.dax_job import DAXJob


class DAXPrintJob(DAXJob):

    def result(self, _program_callback=None):
        return super().result(print)

    def get_raw_data(self, _fname):
        shots = int(self.qobj.config.shots)
        total_cregs = sum(map(lambda x: x[1], self.qobj.experiments[0].header.creg_sizes))
        raw = [[0] for _creg in range(total_cregs) for _s in range(shots)]
        return raw
