from qiskit import *
from qiskit.providers.dax import DAX
from math import pi
from qiskit.circuit.library.standard_gates import MSGate
from qiskit.circuit.library.generalized_gates import GMS


dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

q = QuantumRegister(3)
c = ClassicalRegister(3)
qc = QuantumCircuit(q, c)

XXX1 = GMS(num_qubits=3, theta=[[0, pi, pi],
                                [0, 0, pi],
                                [0, 0, 0]])

xx = GMS(num_qubits=2, theta=[[0, pi],
                                [0, 0]])
qc.append(xx, q[:2])
# print(xx.__getattribute_)

# qc.append(XXX1, q)

qc.measure_all()


backend.load_config("resources.toml")
dax_result = execute(qc, backend, shots=10)
dax_result.print_dax()



