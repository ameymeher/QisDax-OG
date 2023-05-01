import json

algos = ['bv', 'dj', 'ghz', 'grover', 'simon']

jdict = {k: {} for k in algos}

for algo in algos:
    fname = f'{algo}.aria.parallel.txt'
    store = []
    with open(fname, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                store.append(abs(eval(line)))
    jdict[algo]['parallel_rt'] = store
    
    fname = f'{algo}.aria.serial.txt'
    store = []
    with open(fname, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                store.append(abs(eval(line)))
    jdict[algo]['linear_rt'] = store

    fname = f'{algo}.cryo.maxwidth.txt'
    store = []
    with open(fname, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                a,b = line.split('-')
                if a == 'S':
                    jdict[algo]['cryo_linear_rt'] = int(b.strip())
                elif a == 'W':
                    store.append(int(b.strip()))
    jdict[algo]['cryo_parallel_rt'] = store

    with open(fname, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                a,b = line.split('-')
                if a == 'L':
                    jdict[algo]['linear'] = int(b.strip())
                elif a == 'M':
                    store.append(int(b.strip()))
    jdict[algo]['parallel'] = store

    fname = f'{algo}.aria.maxwidth.txt'
    store = []
    with open(fname, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                a,b = line.split('-')
                if a == 'S':
                    jdict[algo]['aria_linear_rt'] = int(b.strip())
                elif a == 'W':
                    store.append(int(b.strip()))
    jdict[algo]['aria_parallel_rt'] = store

with open('qisdax.json', 'w', encoding="utf-8") as f:
    json.dump(jdict, f, indent=2)