from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') # backend is a job

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)
qc.h(2)
qc.measure([0,1], [0,1])

backend.load_config("resources.toml")
result = execute(qc, backend, shots=10).print_dax()

qc.measure_all()
