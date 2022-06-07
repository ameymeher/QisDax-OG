from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 

q= QuantumRegister(2)
c= ClassicalRegister(2)
qc = QuantumCircuit(q, c)

qc.h(q[0])
qc.h(q[1])

qc.measure_all()

backend.load_config("resources.toml")
dax_job = execute(qc, backend, shots=1000, optimization_level=0)
res = dax_job.result()
counts = res.get_counts()
print(counts)


#Show super basic 
#Show shots
#Show parallel with resource limits
#show parallel with 