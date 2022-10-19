from time import process_time_ns
from qiskit import QuantumCircuit, execute
from qiskit.providers.dax import DAX

def initialize_s(qc, qubits):
    """Apply a H-gate to 'qubits' in qc"""
    for q in qubits:
        qc.h(q)
    return qc


qc = QuantumCircuit(3)
qc.cz(0, 2)
qc.cz(1, 2)
oracle_ex3 = qc


def diffuser(nqubits):
    qc = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range(nqubits):
        qc.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range(nqubits):
        qc.x(qubit)
    # Do multi-controlled-Z gate
    qc.h(nqubits-1)
    qc.mct(list(range(nqubits-1)), nqubits-1)  # multi-controlled-toffoli
    qc.h(nqubits-1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range(nqubits):
        qc.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range(nqubits):
        qc.h(qubit)
    # We will return the diffuser as a gate
    U_s = qc
    return U_s

n = 3
grover_circuit = QuantumCircuit(n)
grover_circuit = initialize_s(grover_circuit, [0,1,2])
grover_circuit += oracle_ex3
grover_circuit += diffuser(n)
grover_circuit.measure_all()

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 
backend.load_config("resources.toml")
with open('profile.txt', 'a') as f:
    f.write(str(process_time_ns()))
dax_job = execute(grover_circuit, backend, shots=512, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)