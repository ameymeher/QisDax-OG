with open(r'/home/kaustubh/dev/qisdax/tests/profile.txt') as f:
    lines = f.readlines()

ss = []

for line in lines:
    val = -eval(line) / pow(10, 6)
    ss.append(val)
    print(val)
    if len(ss) == 5:
        print('Avg', sum(ss) / 5)
        ss = []
    