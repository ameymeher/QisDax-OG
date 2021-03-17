from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

num_bits = 4

q= QuantumRegister(num_bits)
c= ClassicalRegister(num_bits)
qc = QuantumCircuit(q, c)

qc.h(q)

qc.measure(list(range(num_bits)), list(range(num_bits)))

backend.load_config("resources.toml")
#print(qc.qasm())
dax_result = execute(qc, backend, shots=1000)
dax_result.print_dax()

