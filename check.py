import os

fin = open('input/output.txt', 'r')
fout = open('output/output.txt', 'r')
R = 0
W = 0
r = 0
w = 0
il = fin.readline()
ol = fout.readline()
il = fin.readline().strip()
ol = fout.readline().strip()
if il == ol:
    R += 1
else:
    W += 1
for i in range(len(il)):
    if il[i] == ol[i]:
        r += 1
    else:
        w += 1


while il != '':
    il = fin.readline()
    ol = fout.readline()
    il = fin.readline().strip()
    ol = fout.readline().strip()
    if il == ol:
        R += 1
    else:
        W += 1
    for i in range(len(il)):
        if il[i] == ol[i]:
            r += 1
        else:
            w += 1

fin.close()
fout.close()

print('Character-wise accuracy: ' + str(r/(r+w)) + ' Sentence-wise accuracy: ' + str(R/(R+W)))