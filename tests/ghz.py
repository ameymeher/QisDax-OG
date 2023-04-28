from time import process_time_ns
from qiskit import execute, QuantumCircuit

from qiskit.providers.dax import DAX

# Number of qubits
N = 3

def cx_it(q_c, i, j):
    import math
    q_c.ry(math.pi /2, i)
    q_c.rxx(math.pi / 2, i, j)
    q_c.ry(-math.pi / 2, i)
    q_c.rx(-math.pi / 2, j)
    q_c.rz(-math.pi / 2, i)

# Create a circuit with a register of N qubits
circ = QuantumCircuit(N)
# H gate on qubit 0, putting this qubit in a superposition of |0> + |1>.
circ.h(0)

for i in range(1, N):
# A CX (CNOT) gate on control qubit 0 and target qubit i.
    # circ.cx(0, i)
    cx_it(circ, 0, i)

circ.measure_all()


dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 
backend.load_config("resources.toml")
with open('profile.txt', 'a') as f:
    f.write(str(process_time_ns()))
dax_job = execute(circ, backend, shots=512, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)