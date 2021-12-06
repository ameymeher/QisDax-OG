from qiskit import *
from qiskit.providers.dax import DAX
from math import pi
from qiskit.circuit.library.standard_gates import MSGate
# from qiskit.circuit.library.generalized_gates import GMS


dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

q = QuantumRegister(4)
c = ClassicalRegister(4)
qc = QuantumCircuit(q, c)


qc.ms(pi, q[:3])
qc.ms(pi/4, q[:3])
xx = MSGate(num_qubits=2, theta=pi/4)
qc.append(xx, q[:2])

# qc.ms(q[0:2], pi)
qc.measure_all()


backend.load_config("resources.toml")
dax_result = execute(qc, backend, shots=10)
dax_result.print_dax()



