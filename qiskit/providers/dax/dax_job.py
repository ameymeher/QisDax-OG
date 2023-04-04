# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=protected-access

from collections import Counter
import os
from tempfile import gettempdir
from uuid import uuid4
import numpy as np


from qiskit.providers import BaseJob
from qiskit.result import Result
from jinja2 import Environment, FileSystemLoader


class DAXJob(BaseJob):
    def __init__(self, backend, job_id=str(uuid4()), qobj=None, dax_code=None, creg_indices=None):
        super().__init__(backend, job_id)
        self._backend = backend        
        self.qobj = qobj
        self.dax_code = dax_code
        self._job_id = job_id        
        self.creg_indices = creg_indices
    
    def get_raw_data(self, fname):
        return None

    def get_result_counts(self, raw_data):
        shots = int(self.qobj.config.shots)
        total_cregs = sum(map(lambda x: x[1], self.qobj.experiments[0].header.creg_sizes))
        raw_reshaped = np.asarray(raw_data).flatten().reshape((shots, -1)).tolist()
        creg_reshaped = np.asarray(self.creg_indices).flatten().tolist()
        hexes = []
        for shot_record in raw_reshaped:
            result_counter = [0 for _ in range(total_cregs)]
            for measurement, creg_idx in zip(shot_record, creg_reshaped):
                result_counter[total_cregs - creg_idx - 1] = 1 if measurement else 0
            hexes.append(hex(int(''.join(map(str, result_counter)), 2)))
        return dict(Counter(hexes))
 
    def result(self, program_callback = None): 
        dax_program = self.get_dax()
        if program_callback:
            program_callback(dax_program)
        fname = os.path.join(gettempdir(), f'qisdax-{self._job_id}.py')

        with open(fname, 'w', encoding="utf-8") as f:
            f.write(dax_program)

        raw = self.get_raw_data(fname)
        return self.get_result_obj(raw_data=raw) 


    def get_result_obj(self, raw_data):
        results = [
            {
                'success': True,
                'shots': self.qobj.config.shots,
                'data': {
                    'counts':self.get_result_counts(raw_data=raw_data)
                },
                'header': self.qobj.experiments[0].header.to_dict(),
            }]

        return Result.from_dict({
            'results': results,
            'backend_name': self._backend._configuration.backend_name,
            'backend_version': self._backend._configuration.backend_version,
            'qobj_id': self.qobj.qobj_id,
            'success': True,
            'job_id': self._job_id,
        })


    def get_dax(self):

        file_loader = FileSystemLoader(searchpath="../qiskit/providers/dax")        
        env = Environment(loader=file_loader)
        template = env.get_template('dax_jinja.j2')

        num_qubits = self.qobj.to_dict()["config"]["n_qubits"]

        dax_program = template.render(
            shots=self.qobj.config.shots, instructions_list=self.dax_code, qubits=num_qubits)

        return dax_program

    def cancel(self):
        pass

    def status(self):
        return 'success'        

    def submit(self):
        pass
