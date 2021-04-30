from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

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

backend.load_config("new_resources.toml")
dax_result = execute(qc, backend, shots=1000)
dax_result.print_dax()

