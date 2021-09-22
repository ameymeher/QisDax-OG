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

# To add new gate implementation, you must add the name of the gate to the 'decoding_dict',
# and add it to dax_backend.py 'basis_gates# '.


import json

from numpy import pi

# global_var = 0

#[h0, h1n ==]
# [h0, h1 ]
# x1
# [[h0, x1], h1 ]
#{id:(line, {id3:(line3, {}), id4:(line4, {})}), id2:(line2, {}), id5:..}
# y0
# x2

# [[h0, [x1, y0]], h1 ]
# [[h0, x1], [h1, y0] ]

    #_add_depend(depends, rem[0][4], instr_count, line)
    # depends   == array of quantum gates shaped after scheduling
    # src       == rem[0][4] == id for the 0th element in the remove array
    # instr_count == id for the element we are adding
    # line      == dax code string
def _add_depend(depends, src, dest, line):
    if src in depends:
        depends[src][1][dest] = (line, {})
        return 1
    for k, v in depends.items():
        if _add_depend(v[1], src, dest, line):
            return 1
    return 0
   

#{id:(line, {id3:(line3, {}), id4:(line4, {})}), id2:(line2, {}), id5:..}
def _serialize_timeline(ops, depends, level = 0):
    if len(depends) > 1:
        ops.append(level*"\t" + "with parallel:")
        level += 1

    for k, v in depends.items():
        temp = []
        _serialize_timeline(temp, v[1], level)
        
        if len(depends) > 1 and len(temp) > 0:
            ops.append(level*"\t" + "with sequential:")
            level += 1
            temp = []
            _serialize_timeline(temp, v[1], level)

        ops.append(level*"\t" + v[0])
        ops += [t for t in temp if len(t) > 0]

        if len(depends) > 1 and len(temp) > 0:
            level -= 1



def _schedule_experiment(instr_count, active_gates, lookahead, rem, depends, decoding_dict, gate_resources, lookahead_qbits_list, instruction_queue):
    # global global_var
    while True:

        if lookahead >= len(instruction_queue): 
            break
           
        inst = instruction_queue[lookahead]
                  
        op_qbits = inst["qubits"]
        gate_name = inst["name"]
        line = inst["line"]        

        instr_count, lookahead, lookahead_qbits_list = _schedule_instruction(op_qbits, instr_count, active_gates, instruction_queue,
             lookahead, rem, depends, decoding_dict, gate_resources, lookahead_qbits_list, line, gate_name)                        
    return instr_count, lookahead, lookahead_qbits_list, instruction_queue


def _schedule_instruction(op_qbits, instr_count, active_gates, instruction_queue, lookahead, rem, depends,
 decoding_dict, gate_resources, lookahead_qbits_list, line, gate_name):                        
    # Get resource information
    if gate_resources is not None:
        resource = gate_resources.get(gate_name, {})
        time = resource.get("time", 1)
        mirrors = resource.get("mirrors", 1)
        lasers = resource.get("lasers", 1)
        size = {"mirrors":mirrors, "lasers":lasers}
        total_mirrors = gate_resources.get("total_mirrors", 3)
        total_lasers = gate_resources.get("total_lasers", 3)
        cap = {"mirrors":total_mirrors, "lasers":total_lasers}

    else:
        raise ValueError("Please specify a resource file")
    
    # Check if we have the resources now
    depend_check = len(set(op_qbits).intersection(
        set([t for x in active_gates for t in x[2]]))) > 0

    #catches instructions that are too 'large'
    # resource_check = cap - sum([x[1] for x in active_gates]) < size

    resource_check = any([ ((cap[res] - sum([x[1][res] for x in active_gates])) < size[res]) for res in cap.keys() ])

    
    # catches the instructions that depend on an instruction that was skipped
    lookahead_check = len(set(op_qbits).intersection(set(lookahead_qbits_list))) > 0 

    if depend_check or resource_check or lookahead_check:
        #print(depend_check,resource_check,lookahead_check)
        lookahead += 1
        lookahead_qbits_list += op_qbits        
        return instr_count, lookahead, lookahead_qbits_list
    
    
    active_gates.append((time, size, op_qbits, line, instr_count))
    # experiment.instructions.pop(lookahead)
    instruction_queue.pop(lookahead)
    
    if len(rem) == 0:
        depends[instr_count] = (line, {})
    else:
        _add_depend(depends, rem[0][4], instr_count, line)
    instr_count += 1
   
    return instr_count, lookahead, lookahead_qbits_list


def _experiment_to_seq(experiment, gate_resources):
    depends = {}
    instr_count = 0
    active_gates = []
    meas = 0
    ops = []
    instruction_queue = []

    def std_replace(inst_name):
        def test(inst):        
            return [{"line": "self.q.{}({})".format(inst_name, ",".join(getattr(inst, "params", [])) + ",".join(map(str, inst.qubits))),
                     "qubits": inst.qubits,
                     "name": inst.name}]
        return test

    def custom_cx():
        def decompose(inst):
            return [
                {
                    "line": "self.q.ry(self.pi/2,{})".format(inst.qubits[0]),
                    "qubits": [inst.qubits[0]],
                    "name": "ry"
                },
                { 
                # xx4 == rxx(pi/4)
                    "line": "self.q.xx4({},{})".format(inst.qubits[0], inst.qubits[1]),
                    "qubits": inst.qubits,
                    "name": "xx4"
                },
                {
                    "line": "self.q.ry(-self.pi/2,{})".format(inst.qubits[0]),
                    "qubits": [inst.qubits[0]],
                    "name": "ry"
                },                
                {
                    "line": "self.q.rx(-self.pi/2,{})".format(inst.qubits[1]),
                    "qubits": [inst.qubits[1]],
                    "name": "rx"
                },
                                {
                    "line": "self.q.p(-self.pi/2,{})".format(inst.qubits[0]),
                    "qubits": [inst.qubits[0]],
                    "name": "p"
                },
            ]
        return decompose

    def custom_ms():
        def decompose(inst):
            print(inst)
            return [                
                {
                    "line": "self.q.ms({},{},{})".format(inst.params[0], inst.qubits[0], inst.qubits[1]),
                    "qubits": inst.qubits,
                    "name": "ms"
                },
            ]
        return decompose

    def custom_gms():
        def decompose(inst):
            # print(dir(inst))
            # print(inst.__reduce_ex__)
            if len(inst.qubits) == 2:

                return [                
                    {
                    "line": "self.q.gms2()",
                    "qubits": inst.qubits,
                    "name": inst.name
                },
                ]
            if len(inst.qubits) == 3:

                return [                
                    {
                    "line": "self.q.gms3()",
                    "qubits": inst.qubits,
                    "name": inst.name
                },
                ]
            

            return [                
                {
                    "line": "self.q.gms()",
                    "qubits": inst.qubits,
                    "name": inst.name
                },
            ]
        return decompose

    def custom_rx():
        def decompose(inst):
            return [                
                {
                    "line": "self.q.rx({},{})".format(inst.params[0], inst.qubits[0]),
                    "qubits": inst.qubits,
                    "name": "inst.name"
                },
            ]
        return decompose

    def custom_ry():
        def decompose(inst):
            return [                
                {
                    "line": "self.q.ry({},{})".format(inst.params[0], inst.qubits[0]),
                    "qubits": inst.qubits,
                    "name": "inst.name"
                },
            ]
        return decompose

    def custom_rz():
        def decompose(inst):
            return [                
                {
                    "line": "self.q.rz({},{})".format(inst.params[0], inst.qubits[0]),
                    "qubits": inst.qubits,
                    "name": "inst.name"
                },
            ]
        return decompose

    def custom_rxx():
        def decompose(inst):
            if (inst.params[0] == (pi / 4)):

                #  xx4 == rxx(pi/4)
                returnVal = [                
                    {
                        "line": "self.q.xx4({},{})".format(inst.qubits[0], inst.qubits[1]),
                        "qubits": inst.qubits,
                        "name": "inst.name"
                    },
                ]
            
            else:
                returnVal = [                
                    {
                        "line": "self.q.rxx({},{},{})".format(inst.params[0], inst.qubits[0], inst.qubits[1]),
                        "qubits": inst.qubits,
                        "name": "inst.name"
                    },
                ]
            
            return returnVal
        return decompose

    def barrier_func():
        def noop(inst):
            return [{"line": "# Barrier was here", "qubits": inst.qubits, "name": inst.name}]
        return noop

    decoding_dict = {        
        "id": std_replace("id"), 
        "x": std_replace("x"), 
        "y": std_replace("y"), 
        "z": std_replace("z"), 
        "h": std_replace("h"), 
        "rx": custom_rx(), 
        "ry": custom_ry(), 
        "rz": custom_rz(),
        "barrier": barrier_func(),
        "cx": custom_cx(),
        "rxx": custom_rxx(),
        "ms": custom_ms(),
        "gms": custom_gms(),
        #todo: "cz": std_decompose("cz")
    }    
    
    # remove/rem -> remove_
    # lookahead ->
    # lookahead qbits list -> 
    while len(experiment.instructions):      
        inst = experiment.instructions.pop(0)  
        if inst.name == 'measure':                        
            continue

        try:   
            instruction_queue += decoding_dict[inst.name](inst)                                     
        except:        
            raise Exception("Operation '%s' outside of basis id, x, y, z, h, rx, ry, rz, rxx, cx, cz, ms, gms, barrier" % inst.name)
        

    while True:

        if len(active_gates) == 0 and len(instruction_queue) == 0:
            break

        # Clear out unused things
        # removes the gates that just finished execution from active_gates
        remove = []
        for i, x in enumerate(active_gates):            
            active_gates[i] = (x[0] - 1, *x[1:5])
            if x[0] == 0:
                remove.append(active_gates[i])
        for x in remove:
            active_gates.remove(x)
            
        lookahead = 0
        lookahead_qbits_list = []
        

        instr_count, lookahead, lookahead_qbits_list, instruction_queue = _schedule_experiment(instr_count, active_gates, lookahead,
         remove, depends, decoding_dict, gate_resources, lookahead_qbits_list, instruction_queue)

    _serialize_timeline(ops, depends)

    return ops


def qobj_to_dax(qobj, shots, gate_resources):
    """Return a list of DAX code strings in a qobj

    If we were actually working with the hardware we would be executing these code strings
    to build a real kernel in DAX.

    """

    if len(qobj.experiments) > 1:
        raise Exception    

    return _experiment_to_seq(qobj.experiments[0], gate_resources)
