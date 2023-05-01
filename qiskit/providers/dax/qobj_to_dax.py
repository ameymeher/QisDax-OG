from os import getenv
from typing import Dict, Generator, List, Tuple
from qiskit.qobj import QasmQobj, QasmQobjExperiment, QasmQobjInstruction


def _should_add(instruction: QasmQobjInstruction, layer: List[List[QasmQobjInstruction]], is_first_gate: bool, max_layer_width: int, gate_resources: Dict) -> Tuple[bool, int]:
    if is_first_gate:
        return True, _get_width(inst_queue=[instruction], gate_resources=gate_resources)
    current_layer_width = max([_get_width(layer[q_index], gate_resources=gate_resources) for q_index in instruction.qubits])
    new_layer_width = max([_get_width(inst_queue=layer[q_index]+[instruction], gate_resources=gate_resources) for q_index in instruction.qubits])
    return abs(new_layer_width - max_layer_width) < abs(current_layer_width - max_layer_width), new_layer_width


def _get_width(inst_queue: List[QasmQobjInstruction], gate_resources: Dict) -> int:
    relative_time = list(
        map(int, gate_resources.get('relative_time').split(',')))
    return sum([relative_time[len(inst.qubits) - 1] if inst.name != 'barrier' else 0 for inst in inst_queue])


def _get_qbit_indices(qbit_seq: Tuple[List[QasmQobjInstruction]], next_idxs: List[int], gate_resources: Dict) -> List[int]:
    qbit_sorted = sorted(enumerate(qbit_seq), key=lambda x: _get_width(
        inst_queue=x[1][next_idxs[x[0]]:], gate_resources=gate_resources), reverse=True)
    indices = [item[0] for item in qbit_sorted]
    return indices


def _resource_count(layer: List[List[QasmQobjInstruction]], gate_resources: Dict) -> Dict[str, int]:
    lasers_req = 0
    mirrors_req = 0
    for iq, q in enumerate(layer):
        laser_max = max(
            [0]+[gate_resources.get(inst.name, {}).get('lasers', 0) for inst in q if iq == min(inst.qubits)])
        lasers_req += laser_max
        mirror_max = max(
            [0]+[gate_resources.get(inst.name, {}).get('mirrors', 0) for inst in q if iq == min(inst.qubits)])
        mirrors_req += mirror_max
    return {'mirrors': mirrors_req, 'lasers': lasers_req}


def _resource_check(to_check: Dict, gate_resources: Dict) -> bool:
    return all([gate_resources.get(f'total_{k}', 0) >= to_check.get(k) for k in to_check.keys()])


def _get_parallel_layer(qbit_seq: Tuple[List[QasmQobjInstruction]], gate_resources: Dict) -> Generator[List[List[QasmQobjInstruction]], None, None]:
    next_idxs = [0 for _ in qbit_seq]
    total_gates = [len(seq) for seq in qbit_seq]
    while next_idxs != total_gates:
        first_gate = [True for _ in qbit_seq]
        width_checked = [False for _ in qbit_seq]
        layer = [[] for _ in qbit_seq]
        max_layer_width = 0
        resource_exhausted = False
        while not (all(width_checked) or resource_exhausted):
            for qbit_idx in _get_qbit_indices(qbit_seq=qbit_seq, next_idxs=next_idxs, gate_resources=gate_resources):
                seq = qbit_seq[qbit_idx]
                if next_idxs[qbit_idx] == total_gates[qbit_idx]:
                    width_checked[qbit_idx] = True
                    continue
                instruction = seq[next_idxs[qbit_idx]]
                for participant in instruction.qubits:
                    if qbit_seq[participant][next_idxs[participant]] != instruction:
                        width_checked[qbit_idx] = True
                        break
                else:
                    is_first_gate = all(first_gate[q]
                                        for q in instruction.qubits)
                    should_add, new_width = _should_add(
                        instruction=instruction, layer=layer, is_first_gate=is_first_gate, max_layer_width=max_layer_width, gate_resources=gate_resources)
                    if should_add:
                        for participant in instruction.qubits:
                            layer[participant].append(instruction)
                        resource_count = _resource_count(
                            layer=layer, gate_resources=gate_resources)
                        resource_check = _resource_check(
                            to_check=resource_count, gate_resources=gate_resources)
                        if resource_check:
                            for participant in instruction.qubits:
                                next_idxs[participant] += 1
                                if new_width > max_layer_width:
                                    max_layer_width = new_width
                                    for width_idx in range(len(width_checked)):
                                        width_checked[width_idx] = width_idx in instruction.qubits
                                elif new_width == max_layer_width:
                                    for width_idx in instruction.qubits:
                                        width_checked[width_idx] = True
                        else:
                            for participant in instruction.qubits:
                                layer[participant].pop()
                            resource_exhausted = True
                            break
                        for participant in instruction.qubits:
                            first_gate[participant] = False
                    else:
                        for participant in instruction.qubits:
                            width_checked[participant] = True
        with open('maxwidth.txt', 'a') as f:
            f.write(f'W-{max_layer_width}\n')
        with open('maxwidth.txt', 'a') as f:
            f.write(f'M-{max(len(seq) for seq in layer)}\n')
        yield layer


def _get_qbit_sequences(experiment: QasmQobjExperiment) -> Tuple[List[QasmQobjInstruction]]:
    num_qubits: int = max(max(instruction.qubits)
                          for instruction in experiment.instructions) + 1
    qbit_seq: Tuple[List[QasmQobjInstruction]] = tuple(
        [] for _ in range(num_qubits))
    for idx in range(len(experiment.instructions)):
        instruction: QasmQobjInstruction = experiment.instructions[idx]
        for qubit in instruction.qubits:
            qbit_seq[qubit].append(instruction)
    return qbit_seq


def _get_parallelized_layers(experiment: QasmQobjExperiment, gate_resources: Dict) -> Tuple[List[List[QasmQobjInstruction]]]:
    qubit_seq = _get_qbit_sequences(experiment=experiment)
    return tuple(_get_parallel_layer(
        qbit_seq=qubit_seq, gate_resources=gate_resources))


def _merge_lines(multi_qubit_pairing: Tuple[int], layer: List[List[QasmQobjInstruction]]) -> List[List[List[QasmQobjInstruction]]]:
    serial_block: List[List[List[QasmQobjInstruction]]] = []
    track_index = {}
    for q in multi_qubit_pairing:
        track_index[q] = 0
    while not all([track_index[q] == len(layer[q]) for q in multi_qubit_pairing]):
        parallel_block: List[List[QasmQobjInstruction]] = []
        multi_gate = None
        for q in multi_qubit_pairing:
            if track_index[q] >= len(layer[q]):
                break
            curr_gate = layer[q][track_index[q]]
            if multi_gate is not None and multi_gate != curr_gate:
                break
            multi_gate = curr_gate
        else:
            serial_block_inner: List[QasmQobjInstruction] = []
            inst = layer[multi_qubit_pairing[0]
                         ][track_index[multi_qubit_pairing[0]]]
            serial_block_inner.append(inst)
            parallel_block.append(serial_block_inner)
            for q in inst.qubits:
                track_index[q] += 1
            serial_block.append(parallel_block)
            continue

        for qb in multi_qubit_pairing:
            serial_block_inner: List[QasmQobjInstruction] = []
            while True:
                if track_index[qb] >= len(layer[qb]):
                    break
                inst = layer[qb][track_index[qb]]
                if len(inst.qubits) > 1:
                    break
                serial_block_inner.append(inst)
                track_index[qb] += 1
            parallel_block.append(serial_block_inner)
        serial_block.append(parallel_block)
    return serial_block


def _get_structured(experiment: QasmQobjExperiment, parallelized_layers: Tuple[List[List[QasmQobjInstruction]]]):
    num_qubits: int = max(max(instruction.qubits)
                          for instruction in experiment.instructions) + 1
    outer_parallel: List[List[List[List[List[QasmQobjInstruction]]]]] = []
    for layer in parallelized_layers:
        multi_qubit_gates = [
            inst for seq in layer for inst in seq if len(inst.qubits) > 1]
        multi_qubit_pairing_set = set(
            [tuple(inst.qubits) for inst in multi_qubit_gates])
        for q in range(num_qubits):
            count = len([a for a in multi_qubit_pairing_set if q in a])
            if count > 1:
                raise Exception("Unable to convert this timeline to DAX")
        structured: List[List[List[List[QasmQobjInstruction]]]] = []
        processed = [False for _ in range(num_qubits)]
        for multi_qubit_pairing in multi_qubit_pairing_set:
            structured.append(_merge_lines(
                multi_qubit_pairing=multi_qubit_pairing, layer=layer))
            for q in multi_qubit_pairing:
                processed[q] = True
        for idx, val in enumerate(processed):
            if not val:
                structured.append([[layer[idx]]])
        outer_parallel.append(structured)
    return outer_parallel

def _get_linear_structured(experiment: QasmQobjExperiment):
    return [[[[experiment.instructions]]]]


def _std_replace(instruction: QasmQobjInstruction) -> str:
    return f'self.q.{_get_dax_gate(instruction.name)}({",".join(tuple(map(str, getattr(instruction, "params", []))) + tuple(map(str, instruction.qubits)))})'


def _commented(instruction: QasmQobjInstruction) -> str:
    return '# ' + _std_replace(instruction=instruction)


def _get_dax_gate(name: str):
    nonstandard_names = {
        'cx': 'cnot',
        'sdg': 'sqrt_z_dag',
        's': 'sqrt_z',
        'sx': 'sqrt_x',
        'sxdg': 'sqrt_x_dag',
    }
    return nonstandard_names.get(name, name)


def _get_instr_str(instruction: QasmQobjInstruction) -> List[str]:
    name = _get_dax_gate(instruction.name)
    allowed_gates = ['i', 'x', 'y', 'z', 'h', 'sqrt_x', 'sqrt_x_dag', 'sqrt_y', 'sqrt_y_dag',
                     'sqrt_z', 'sqrt_z_dag', 'rx', 'ry', 'rz', 'rphi', 'xx', 'xx_dag', 'rxx', 'cz', 'cnot']
    if name in allowed_gates:
        return [_std_replace(instruction=instruction)]
    elif instruction.name == 'measure':
        return [f'self.q.m_z({instruction.qubits[0]})']
    else:
        return [_commented(instruction=instruction)]

def _store_creg_info(instruction: QasmQobjInstruction, creg_indices: List[int]):
    return creg_indices + [instruction.memory[0]]


def _get_qasm_data(experiment: QasmQobjExperiment, parallelized_layers: Tuple[List[List[QasmQobjInstruction]]]) -> Tuple[List[str], List[int]]:
    TAB_WIDTH = getenv('TAB_WIDTH', 4)
    outer_parallels = _get_structured(
        experiment=experiment, parallelized_layers=parallelized_layers)
    # outer_parallels = _get_linear_structured(experiment)
    result = []
    to_remove_outer_parallel = []
    for outer_parallel_idx, outer_parallel in enumerate(outer_parallels):
        to_remove_seq = []
        for seq_idx, seq in enumerate(outer_parallel):
            to_remove_parallel = []
            for parallel_idx, parallel in enumerate(seq):
                to_remove_inner_seq = []
                for inner_seq_idx, inner_seq in enumerate(parallel):
                    if len(inner_seq) == 0:
                        to_remove_inner_seq.append(inner_seq_idx)
                for inner_seq_idx in reversed(to_remove_inner_seq):
                    del parallel[inner_seq_idx]
                if len(parallel) == 0:
                    to_remove_parallel.append(parallel_idx)
            for parallel_idx in reversed(to_remove_parallel):
                del seq[parallel_idx]
            if len(seq) == 0:
                to_remove_seq.append(seq_idx)
        for seq_idx in reversed(to_remove_seq):
            del outer_parallel[seq_idx]
        if len(outer_parallel) == 0:
            to_remove_outer_parallel.append(outer_parallel_idx)
    for outer_parallel_idx in reversed(to_remove_outer_parallel):
        del outer_parallels[outer_parallel_idx]
    
    creg_indices = []
    depth = 0
    for outer_parallel in outer_parallels:
        outer_parallel_depth = depth
        outer_parallel_scope = len(outer_parallel) > 1
        if outer_parallel_scope:
            result.append('with parallel:')
            outer_parallel_depth += 1
        for seq in outer_parallel:
            seq_depth = outer_parallel_depth
            seq_scope = len(seq) > 1 or any(inst.name == 'measure' for parallel in seq for inner_seq in parallel for inst in inner_seq)
            if seq_scope:
                result.append(TAB_WIDTH*outer_parallel_depth*' ' + 'with sequential:')
                seq_depth += 1
            for parallel in seq:
                creg_combined = []
                q_indices = []
                parallel_depth = seq_depth
                parallel_scope = len(parallel) > 1
                if parallel_scope:
                    result.append(TAB_WIDTH*seq_depth*' ' + 'with parallel:')
                    parallel_depth += 1
                for inner_seq in parallel:
                    inner_seq_depth = parallel_depth
                    inner_seq_scope = len(inner_seq) > 1
                    if inner_seq_scope:
                        result.append(TAB_WIDTH*parallel_depth*' ' + 'with sequential:')
                        inner_seq_depth += 1
                    for inst in inner_seq:
                        for inst_line in _get_instr_str(instruction=inst):
                            result.append(TAB_WIDTH*inner_seq_depth*' ' + inst_line)
                        if inst.name == 'measure':
                            q_indices.append(inst.qubits[0])
                            creg_combined = _store_creg_info(inst, creg_indices=creg_combined)
                    result.append(TAB_WIDTH*inner_seq_depth*' ' + 'pass')
                if creg_combined:
                    creg_indices.append(creg_combined)
                    result.append(TAB_WIDTH*seq_depth*' ' + f'self.q.store_measurements({q_indices})')
    return result, creg_indices


def _experiment_to_seq(experiment: QasmQobjExperiment, gate_resources: Dict) -> Tuple[List[str], List[int]]:
    with open('maxwidth.txt', 'w') as f:
        f.write('')
    parallelized_layers = _get_parallelized_layers(
        experiment=experiment, gate_resources=gate_resources)
    qasm_strings, creg_indices = _get_qasm_data(experiment=experiment,
                                     parallelized_layers=parallelized_layers)
    with open('maxwidth.txt', 'a') as f:
        w = _get_width(experiment.instructions, gate_resources=gate_resources)
        f.write(f'S-{w}\n')
        f.write(f'L-{max(len(experiment.instructions))}\n')
    return qasm_strings, creg_indices


def qobj_to_dax(qobj: QasmQobj, gate_resources):
    """Return a list of DAX code strings in a qobj

    If we were actually working with the hardware we would be executing these code strings
    to build a real kernel in DAX.

    """

    if len(qobj.experiments) > 1:
        raise Exception

    return _experiment_to_seq(qobj.experiments[0], gate_resources)
