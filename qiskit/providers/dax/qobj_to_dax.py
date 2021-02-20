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

import json

from numpy import pi

def _add_depend(dep, src, dest, line):
    if src in dep:
        dep[src][1][dest] = (line, {})
        return 1
    for k, v in dep.items():
        if _add_depend(v[1], src, dest, line):
            return 1
    return 0

def _serialize_timeline(ops, depends, level = 0):
    if len(depends) > 1:
        ops.append(level*"\t" + "with parallel:")
        level += 1

    for k, v in depends.items():
        temp = []
        _serialize_timeline(temp, v[1], level)
        
        if len(depends) > 1 and len(temp) > 0:
            ops.append(level*"\t" + "with serial:")
            level += 1
            temp = []
            _serialize_timeline(temp, v[1], level)

        ops.append(level*"\t" + v[0])
        ops += [t for t in temp if len(t) > 0]

        if len(depends) > 1 and len(temp) > 0:
            level -= 1


def _schedule_instruction(time, size, inst, instr_count, resource_log, experiment, lookahead, rem, depends):        
    # Actually execute instruction
    if inst.name == 'id':
        line = 'self.i({})'.format(inst.qubits[0])
    elif inst.name == 'x':
        line = 'self.x({})'.format(inst.qubits[0])
    elif inst.name == 'y':
        line = 'self.y({})'.format(inst.qubits[0])
    elif inst.name == 'z':
        line = 'self.z({})'.format(inst.qubits[0])
    elif inst.name == 'h':
        line = 'self.h({})'.format(inst.qubits[0])
    elif inst.name == 'rx':
        line = 'self.rx({}, {})'.format(inst.params[0], inst.qubits[0])
        #print(inst.params[0])
    elif inst.name == 'ry':
        line = 'self.ry({}, {})'.format(inst.params[0], inst.qubits[0])
    elif inst.name == 'rz':
        line = 'self.rz({}, {})'.format(inst.params[0], inst.qubits[0])
    elif inst.name == 'cx':
        line = 'self.cnot({}, {})'.format(inst.qubits[0], inst.qubits[1])
    elif inst.name == 'cz':
        line = 'self.cz({}, {})'.format(inst.qubits[0], inst.qubits[1])            
    else:
        experiment.instructions.pop(lookahead)
        return instr_count
        #raise Exception("Operation '%s' outside of basis id, x, y, z, h, rx, ry, rz, cx, cz" %
        #                inst.name)            

    resource_log.append((time, size, inst.qubits, line, instr_count))
    experiment.instructions.pop(lookahead)

    if len(rem) == 0:
        depends[instr_count] = (line, {})
    else:
        _add_depend(depends, rem[0][4], instr_count, line)
    instr_count += 1
    print(instr_count)
    return instr_count


def _experiment_to_seq(experiment, gate_resources):
    depends = {}
    instr_count = 0
    resource_log = []

    meas = 0
    ops = []

    while True:

        if len(experiment.instructions) == 0 and len(resource_log) == 0:
            break

        # Clear out unused things
        rem = []
        for i, x in enumerate(resource_log):
            resource_log[i] = (x[0] - 1, *x[1:5])
            if x[0] == 0:
                rem.append(resource_log[i])
        for x in rem:
            resource_log.remove(x)
            
        lookahead = 0
        lookahead_bits = []
        while True:

            if lookahead >= len(experiment.instructions):
                break

            inst = experiment.instructions[lookahead]
            
            # Get resource information
            if gate_resources is not None:
                resource = gate_resources.get(inst.name, {})
                time = resource.get("time", 1)
                size = resource.get("size", 1)
                cap = gate_resources.get("capacity", 3)
            else:
                raise ValueError("Please specify a resource file")

            # Check if we have the resources now
            depend_check = len(set(inst.qubits).intersection(
                set([t for x in resource_log for t in x[2]]))) > 0
            resource_check = cap - sum([x[1] for x in resource_log]) < size
            lookahead_check = len(set(inst.qubits).intersection(set(lookahead_bits))) > 0

            if depend_check or resource_check or lookahead_check:
                lookahead += 1
                lookahead_bits += inst.qubits
                continue

#            if inst.name == 'measure':
#                meas += 1
#                experiment.instructions.pop(lookahead)
#                continue
#            elif inst.name == 'barrier':
#                experiment.instructions.pop(lookahead)
#                continue

            #
            #"self.rx({})".format(",".join(getattr(inst, "params", [])) + ",".join(inst.qubits))                             
            instr_count = _schedule_instruction(time, size, inst, instr_count, resource_log, experiment, lookahead, rem, depends)
    #if not meas:
    #    raise ValueError('Circuit must have at least one measurements.')
    _serialize_timeline(ops, depends)

    return ops


def qobj_to_dax(qobj, shots, gate_resources):
    """Return a list of DAX code strings for each experiment in a qobj

    If we were actually working with the hardware we would be executing these code strings
    to build a real kernel in DAX.

    """

    if len(qobj.experiments) > 1:
        raise Exception

    out = []

    # Setup class
    out.append("from dax.experiment import *")
    out.append("class ConstructedExperiment(EnvExperiment):")

    # Setup Class' build method
    out.append("\tdef build(self):")
    out.append("\t\tself.setattr_device('core')")
    out.append(f"\t\tself.num_iterations = {shots}") # (x = number of shots)
    
    # Setup Class' run method
    out.append("\tdef run():")
    out.append("\t\tself._run()")
    out.append("\t\treturn self.result_list")

    ## Setup kernel
    out.append("\t@kernel")

    # Setup kernel _run() method (never changes)
    out.append("\tdef _run(self):")
    out.append("\t\tfor _ range(self.num_iterations):")
    out.append("\t\t\tr = self._qiskit_kernel()")
    out.append("\t\t\tself._collect_data(r)")

    # Defining _qiskit_kernel() method (this is the QC program)
    out.append("\tkernel")
    out.append("\tdef _qiskit_kernel():")
    for experiment in qobj.experiments:
        # Init ions
        out.append("\t\tself.load_ions({})".format(experiment.config.n_qubits))
        out.append("\t\tself.initialize_all()")
        
        # Add lines
        out += ["\t\t{}".format(l) 
            for l in _experiment_to_seq(experiment, gate_resources)]

    # Add measurement
    out.append("\t\tself.detect_all()")
    out.append("\t\tr = self.measure_all()")
    out.append("\t\treturn r")
    
    return out
