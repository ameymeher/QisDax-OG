from time import process_time_ns
from qiskit import QuantumCircuit, execute
from qiskit.providers.dax import DAX

def cx_it(q_c, i, j):
    import math
    q_c.ry(math.pi /2, i)
    q_c.rxx(math.pi / 2, i, j)
    q_c.ry(-math.pi / 2, i)
    q_c.rx(-math.pi / 2, j)
    q_c.rz(-math.pi / 2, i)

def simon_oracle(b):
    """returns a Simon oracle for bitstring b"""
    b = b[::-1] # reverse b for easy iteration
    n = len(b)
    qc = QuantumCircuit(n*2)
    # Do copy; |x>|0> -> |x>|x>
    for q in range(n):
        # qc.cx(q, q+n)
        cx_it(qc, q, q+n)
    if '1' not in b: 
        return qc  # 1:1 mapping, so just exit
    i = b.find('1') # index of first non-zero bit in b
    # Do |x> -> |s.x> on condition that q_i is 1
    for q in range(n):
        if b[q] == '1':
            # qc.cx(i, (q)+n)
            cx_it(qc, i, (q)+n)
    return qc 


b = '110'

n = len(b)
simon_circuit = QuantumCircuit(n*2, n)

# Apply Hadamard gates before querying the oracle
simon_circuit.h(range(n))    
    
# Apply barrier for visual separation
simon_circuit.barrier()

simon_circuit += simon_oracle(b)

# Apply barrier for visual separation
simon_circuit.barrier()

# Apply Hadamard gates to the input register
simon_circuit.h(range(n))

# Measure qubits
simon_circuit.measure(range(n), range(n))
simon_circuit.draw()

# Calculate the dot product of the results
def bdotz(b, z):
    accum = 0
    for i in range(len(b)):
        accum += int(b[i]) * int(z[i])
    return (accum % 2)

dax = DAX.get_provider() # aqt is a provider

# backend = dax.get_backend('dax_code_simulator') 
backend = dax.get_backend('dax_code_printer') 
backend.load_config("resources.toml")
with open('profile.txt', 'a') as f:
    f.write(str(process_time_ns()))
dax_job = execute(simon_circuit, backend, shots=512, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()

for z in counts:
    print( '{}.{} = {} (mod 2)'.format(b, z, bdotz(b,z)) )
