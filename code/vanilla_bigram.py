import os
import re
import json
import sys
import math
sys.stdout = open('../output/output.txt', 'w')

# 最基本的二元组与viterbi算法

mat_in = open('../data/matrix.json', 'r')
matrix = json.load(mat_in)
mat_in.close()

dictf = open('../data/pin2char.json', 'r')
dic = json.load(dictf)
dictf.close()

occf = open('../data/occur.json', 'r')
occur = json.load(occf)
occf.close()

alpha = 1e-20

def laplacian(matrix:dict):
    for la in matrix.keys():
        if occur[la] == 0:
            for cur in matrix[la].keys():
                matrix[la][cur] = math.log(alpha)
        else:
            for cur in matrix[la].keys():
                if matrix[la][cur] == 0:
                    matrix[la][cur] = math.log(alpha*(occur[cur]+alpha))
                else:
                    matrix[la][cur] = math.log(alpha*occur[cur] + (1-alpha)*matrix[la][cur])

    # return matrix


# Laplacian smoothing
def convert(pinlist:list) -> list:

    t = len(pinlist)
    possen = []
    for p in dic[pinlist[0]]:
        possen.append({})
        possen[0][p] = [math.log(occur[p] + alpha), '']
    
    for i in range(1,t):
        possen.append({}) # possen[i] == {}
        for cur in dic[pinlist[i]]:
            pcur = -float('inf')
            las = ''
            for la in possen[i-1].keys():
                if possen[i-1][la][0] + matrix[la][cur] > pcur:
                    pcur = possen[i-1][la][0] + matrix[la][cur]
                    las = la
            possen[i][cur] = [pcur, las]

    lastchar = ''
    maxpos = float('-inf')
    for te in possen[t - 1].keys():
        if possen[t-1][te][0] > maxpos:
            lastchar = te
            maxpos = possen[t-1][te][0]
    
    result = [lastchar]
    for i in range(1,t):
        lastchar = possen[t-i][lastchar][1]
        result.append(lastchar)
    
    return result

laplacian(matrix)
fin = open('../input/input.txt', 'r')
line = fin.readline()
while line != '':
    pinlist = re.split(' ', line.strip())
    length = len(pinlist)
    for p in pinlist:
        print(p, end=' ')
    print('')
    result = convert(pinlist)
    for i in range(length):
        print(result[length - 1 - i], end='')
    print('')

    line = fin.readline()
