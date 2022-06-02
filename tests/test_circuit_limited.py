from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 

num_bits = 4

q= QuantumRegister(num_bits)
c= ClassicalRegister(num_bits)
qc = QuantumCircuit(q, c)

qc.h(0)
qc.h(1)
qc.x(1)
qc.y(0)
qc.barrier()
qc.y(2)
print(qc.draw(output='text'))
qc.measure(list(range(3)), list(range(3)))

# print(qc.qasm())

backend.load_config("resources.toml")
dax_job = execute(qc, backend, shots=1000, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)

