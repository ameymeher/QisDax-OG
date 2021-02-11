from qiskit import *
from qiskit.providers.dax import DAX

dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') 

q= QuantumRegister(2)
c= ClassicalRegister(2)
qc = QuantumCircuit(q, c)

qc.h(q[0])
qc.h(q[1])

qc.measure_all()

backend.load_config("resources.toml")
dax_result = execute(qc, backend, shots=1000)
dax_result.print_dax()


#Show super basic 
#Show shots
#Show parallel with resource limits
#show parallel with 