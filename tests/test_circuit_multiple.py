from qiskit import *
from qiskit.providers.dax import DAX
from math import pi
dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

# region Basic
q= QuantumRegister(4)
c= ClassicalRegister(4)
qc = QuantumCircuit(q, c)
# endregion

# region DJ algo
qc.h(q[0])
qc.x(q[0])
qc.h(q[1])
qc.h(q[2])
qc.x(q[2])
qc.x(q[3])
qc.h(q[3])
qc.cx(q[0], q[3])
qc.cx(q[1], q[3])
qc.cx(q[2], q[3])
qc.x(q[0])
qc.x(q[2])

# endregion
qc.measure_all()

backend.load_config("resources.toml")
dax_result = execute(qc, backend, shots=30, optimization_level=0)
dax_result.print_dax()

