import os
import sys
# sys.stdout = open('output/result.txt', 'a')

fin = open('input/output.txt', 'r')
fout = open('output/output.txt', 'r')

r = 0
w = 0

il = fin.readline()
ol = fout.readline()

il = fin.readline()
ol = fout.readline()
if il == ol:
    r += 1
else:
    w += 1

while il != '':
    il = fin.readline()
    ol = fout.readline()
    il = fin.readline()
    ol = fout.readline()
    if il == ol:
        r += 1
    else:
        w += 1

fin.close()
fout.close()

print(str(r/(r+w)))
