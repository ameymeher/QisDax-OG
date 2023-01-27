# importing Qiskit
from qiskit import QuantumCircuit, execute

from qiskit.providers.dax import DAX

qc = QuantumCircuit(1)
qc.x(0)
qc.y(0)
qc.sxdg(0)
qc.s(0)
qc.sx(0)
qc.sdg(0)
qc.x(0)
qc.sxdg(0)
qc.measure_all()


dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_artiq_device')
backend.load_config("resources.toml")
dax_job = execute(qc, backend, shots=30, optimization_level=0)
res = dax_job.result()
