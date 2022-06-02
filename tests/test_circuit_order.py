from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 

num_bits = 4

q= QuantumRegister(num_bits)
c= ClassicalRegister(num_bits)
qc = QuantumCircuit(q, c)

qc.x(q[0])
qc.cx(q[0], q[1])
qc.x(q[2])
qc.x(q[3])
qc.cx(q[2], q[3])

qc.measure(list(range(num_bits)), list(range(num_bits)))

backend.load_config("resources.toml")
print(qc.qasm())
dax_job = execute(qc, backend, shots=1000, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)

