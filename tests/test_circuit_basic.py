from qiskit import *
from qiskit.providers.dax import DAX
from math import pi
dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 

q= QuantumRegister(2)
c= ClassicalRegister(2)
qc = QuantumCircuit(q, c)

qc.h(q[0])
qc.cx(q[0], q[1])
qc.y(q[1])

qc.measure_all()


backend.load_config("resources.toml")
dax_job = execute(qc, backend, shots=10, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)

