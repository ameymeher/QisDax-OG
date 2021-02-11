from qiskit import *
from qiskit.providers.dax import DAX


dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_generator') # backend is a job

# TODO: Move away from execute() and use our own function which is clearer i.e. DAX.compile(QuantumCicruit q)
# TODO: Implement execute actually communicating with DAX hardware to deploy kernel to ARTIX

# Pre-baked
def make_kernel(n):

    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.h(2)
    qc.measure([0,1], [0,1])

    backend.load_config("resources.toml")
    dax_func = execute(qc, backend, shots=10).get_function()

    # Example get_function output (very bare bones exact 1:1 code)
    # self.h(0)
    # self.cnot(0, 1)

    @dax
    def diffuser():
        for i in range(n):
            # DAX Code
            dax_func()

    # Diffuser
    # def diffuser(self):
    #    for i in range(n):
    #       self.h(0)
    #       self.cnot(0, 1)

    return diffuser


n = 100
k = make_kernel(n)

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.kernel(k)

dax_code = execute(qc, backend, shots=10).print_dax()

print(dax_code)

# Output:
#
# from dax.experiment import *
# class ConstructedExperiment(EnvExperiment):
#    def build(self):
#        self.setattr_device('core')
#
#    @kernel
#    def run(self):
#        self.load_ions(2)
#        self.initialize_all()
#        
#        for i in range(100):
#            self.h(0)
#            self.cnot(0, 1)
#        
#        self.detect_all()
#        r = self.measure_all()


