# initialization
from time import process_time_ns
import matplotlib.pyplot as plt
import numpy as np

# importing Qiskit
from qiskit import QuantumCircuit, execute

from qiskit.providers.dax import DAX

n = 3 # number of qubits used to represent s
s = '011'   # the hidden binary string

def cx_it(q_c, i, j):
    import math
    q_c.ry(math.pi /2, i)
    q_c.rxx(math.pi / 2, i, j)
    q_c.ry(-math.pi / 2, i)
    q_c.rx(-math.pi / 2, j)
    q_c.rz(-math.pi / 2, i)

# We need a circuit with n qubits, plus one auxiliary qubit
# Also need n classical bits to write the output to
bv_circuit = QuantumCircuit(n+1, n)

# put auxiliary in state |->
bv_circuit.h(n)
bv_circuit.z(n)

# Apply Hadamard gates before querying the oracle
for i in range(n):
    bv_circuit.h(i)
    
# Apply barrier 
bv_circuit.barrier()

# Apply the inner-product oracle
s = s[::-1] # reverse s to fit qiskit's qubit ordering
for q in range(n):
    if s[q] == '0':
        bv_circuit.i(q)
    else:
        # bv_circuit.cx_it(q, n)
        cx_it(bv_circuit, q, n)
        
# Apply barrier 
bv_circuit.barrier()

#Apply Hadamard gates after querying the oracle
for i in range(n):
    bv_circuit.h(i)

# Measurement
for i in range(n):
    bv_circuit.measure(i, i)




dax = DAX.get_provider() # aqt is a provider

# backend = dax.get_backend('dax_code_simulator') 
backend = dax.get_backend('dax_code_printer') 
backend.load_config("resources.toml")
with open('profile.txt', 'a') as f:
    f.write(str(process_time_ns()))
dax_job = execute(bv_circuit, backend, shots=512, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)