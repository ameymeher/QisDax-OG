"""
Program generated on  by QisDax v.
"""

from dax.program import *


class QisDaxProgram(DaxProgram, Experiment):

    def build(self):
        self._num_iterations = 30
        self._num_qubits = 1
        self.update_kernel_invariants('_num_iterations', '_num_qubits')
        self._classical_regs = set()

    def run(self):
        # Check number of qubits
        if self._num_qubits > self.q.num_qubits:
            raise RuntimeError('Circuit requires more qubits than the system supports')

        # Run the kernel
        self._run()

    @kernel
    def _run(self):
        self._qiskit_kernel()

        self.core.wait_until_mu(now_mu())

    @kernel
    def _qiskit_kernel(self):
        with self.data_context:
            for _ in range(self._num_iterations):
                self.core.reset()
                self.q.prep_0_all()

                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.x(0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.y(0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.rx(-1.5707963267948966,0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.rz(1.5707963267949,0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.rx(1.5707963267948966,0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.rz(-1.5707963267949,0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.x(0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.rx(-1.5707963267948966,0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                # self.q.barrier(0)
                                pass
                            pass
                        pass
                    pass
                with parallel:
                    with sequential:
                        with parallel:
                            with sequential:
                                self.q.m_z(0)
                                pass
                            pass
                        self.q.store_measurements([0])
                        pass
                    pass
                
