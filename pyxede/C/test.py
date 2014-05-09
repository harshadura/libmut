import string

# Test savgol

import savgol

f = file("example.csv", "r")
rpm = []
t   = []
line = f.readline()
while len(line) > 0:
    if line[-1] == '\n':
        line = line[:-1]
    line = string.split(line, ",")
    rpm.append(int(line[0]))
    t.append(float(line[1]))
    line = f.readline()


d = savgol.smooth(t, 256, 4)
for i in range(0, len(d)):
    print "%lf, %lf, %lf" % (rpm[i], t[i], d[i])



