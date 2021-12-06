from qiskit import *
from qiskit.providers.dax import DAX
from math import pi
from qiskit.circuit.library.standard_gates import MSGate

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

q = QuantumRegister(3)
c = ClassicalRegister(3)
qc = QuantumCircuit(q, c)

qc.rxx(pi/4, 0, 1)
qc.rxx(pi/2, 0, 1)

qc.measure_all()


backend.load_config("resources.toml")
dax_result = execute(qc, backend, shots=10)
dax_result.print_dax()



