from qiskit import *
from qiskit.providers.dax import DAX
from math import pi
dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

q= QuantumRegister(2)
c= ClassicalRegister(2)
qc = QuantumCircuit(q, c)

qc.h(q[0])
qc.cx(q[0], q[1])
qc.y(q[1])

qc.measure_all()


backend.load_config("resources.toml")
dax_result = execute(qc, backend, shots=10)
dax_result.print_dax()

