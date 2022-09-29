from qiskit import *
from qiskit.providers.dax import DAX
import numpy as np
dax = DAX.get_provider() # aqt is a provider

backend = dax.get_backend('dax_code_simulator') 
# backend = dax.get_backend('dax_code_printer') 

# region Basic
_target_qubit = 0
_num_steps_theta = 5
_num_steps_phi = 10
_num_measurements =10

_thetas = np.linspace(0.0, np.pi, num=_num_steps_theta)

_phis = np.linspace(-np.pi, np.pi, num=_num_steps_phi)

def run(backend, thetas, phis, num_measurements, target_qubit):
    backend.load_config("resources.toml")
    c = []
    for theta in thetas:
        for phi in phis:
            # Run state tomography
            print(f'theta={theta}, phi={phi}')
            c.append(_sqst(backend, theta, phi, num_measurements, target_qubit))
    return c

def _sqst(backend, theta, phi, num_measurements, target_qubit):
    count_store = []
    for basis in ["x", "y", "z"]:
        for _ in range(num_measurements):
            qc, q = _create_state(theta, phi, target_qubit)
            _measure(basis, qc, q, target_qubit)
            dax_job = execute(qc, backend, shots=1, optimization_level=0)
            res = dax_job.result()
            counts = res.get_counts()
            count_store.append(counts)
    return count_store


def _measure(basis, qc, q, target_qubit):
    if basis == "x":  # Change to X basis
        qc.x(q[target_qubit])
    elif basis == "y":  # Change to Y basis
        qc.sdg(q[target_qubit])
        qc.h(q[target_qubit])
        qc.s(q[target_qubit])

    qc.measure_all()

def _create_state(theta, phi, target_qubit):
    q= QuantumRegister(1)
    qc = QuantumCircuit(q)
    qc.ry(theta, q[target_qubit])
    qc.rz(phi, q[target_qubit])
    return qc, q

def analyze(counts, num_measurements, thetas, phis):
    data = np.asarray(tuple(map(lambda x: tuple(map(lambda y: [tuple(y.values())[0]], x)), counts)))

    for d, (theta, phi) in zip(data, ((t, p) for t in thetas for p in phis)):
        # Gather Data
        x_data, y_data, z_data = np.split(d, 3)

        # Based on (nx, ny, nz) = ((nx0 - nx1)/(nx0 + nx1), (ny0 - ny1)/(ny0 + ny1), (nz0 - nz1)/(nz0 + nz1))
        nx = (num_measurements - 2 * np.count_nonzero(x_data)) / num_measurements
        ny = (num_measurements - 2 * np.count_nonzero(y_data)) / num_measurements
        nz = (num_measurements - 2 * np.count_nonzero(z_data)) / num_measurements

        # Convert to measured (r, theta, phi)
        r_avg = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        theta_avg = np.arccos(nz / r_avg) / np.pi
        phi_avg = np.int32(ny / np.abs(ny)) * np.arccos(nx / np.sqrt(nx ** 2 + ny ** 2)) / np.pi

        # Calculate fidelity with desired state
        fidelity = nx * np.sin(theta) * np.cos(phi) + ny * np.sin(theta) * np.sin(phi) + nz * np.cos(theta) + 1
        fidelity /= 2

        print(f'Desired State: (theta, phi) = ({theta}, {phi})')
        print(f'Quantum State: (nx, ny, nz) = ({nx}, {ny}, {nz})')
        print(f'Quantum State: (r, theta, phi) = ({r_avg}, {theta_avg}, {phi_avg}')
        print(f'Fidelity with desired state = {fidelity}')

c = run(backend, _thetas, _phis, _num_measurements, _target_qubit)
analyze(c, _num_measurements, _thetas, _phis)
