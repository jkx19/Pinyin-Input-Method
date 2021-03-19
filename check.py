import os
import sys

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

ref = open('output/result.txt', 'a')
ref.write(str(sys.argv[1:]) + ' ' + str(r/(r+w)) + '\n')
ref.close()