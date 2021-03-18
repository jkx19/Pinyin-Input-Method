import os
import re
import json
import sys
import math
from collections import deque

# Basic bi-gram model with viterbi algorithm
# Considering common words in news
# b, e stand for begin and end.

mat_in = open('../data/word/matrix_w.json', 'r')
matrix = json.load(mat_in)
mat_in.close()

dictf = open('../data/pin2char.json', 'r')
p2c = json.load(dictf)
dictf.close()

occf = open('../data/word/occur.json', 'r')
occur = json.load(occf)
occf.close()

wordf = open('../data/word/wordlist.json', 'r')
p2w = json.load(wordf)
wordf.close()
wordset = set(p2w.keys())

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
def convert(pinlist:list) -> deque:

    t = len(pinlist)
    possen = []
    for i in range(t):
        possen.append({})
    # for p in p2c[pinlist[0]]:
    #     possen.append({})
    #     possen[0][p] = [matrix['e'][p], '']
    
    # for i in range(1,t):
    #     possen.append({}) # possen[i] == {}
    #     for cur in p2c[pinlist[i]]:
    #         pcur = -float('inf')
    #         las = ''
    #         for la in possen[i-1].keys():
    #             if possen[i-1][la][0] + matrix[la][cur] > pcur:
    #                 pcur = possen[i-1][la][0] + matrix[la][cur]
    #                 las = la
    #         possen[i][cur] = [pcur, las]

    i = 0
    while i < t:
        if i == 0:
            if i < t-1 and pinlist[0]+' '+pinlist[1] in wordset:
                for word in p2w[pinlist[0]+' '+pinlist[1]]:
                    possen[1][word] = (matrix['b'][word], -1, 'b')
            for ch in p2c[pinlist[0]]:
                possen[0][ch] = [matrix['e'][ch], -1, 'b']

        else:
            if i < t-1:
                if pinlist[i]+' '+pinlist[i+1] in wordset:
                    for word in p2w[pinlist[i]+' '+pinlist[i+1]]:
                        pcur = -float('inf')
                        las = ''
                        for la in possen[i-1].keys():
                            if possen[i-1][la][0] + matrix[la][word] > pcur:
                                pcur = possen[i-1][la][0] + matrix[la][word]
                                las = la
                        possen[i+1][word] = [pcur, i-1, las]
        
            for cur in p2c[pinlist[i]]:
                pcur = -float('inf')
                las = ''
                for la in possen[i-1].keys():
                    if possen[i-1][la][0] + matrix[la][cur] > pcur:
                        pcur = possen[i-1][la][0] + matrix[la][cur]
                        las = la
                possen[i][cur] = [pcur, i - 1, las]

        i = i + 1


    lastchar = ''
    maxpos = float('-inf')
    for te in possen[t - 1].keys():
        if possen[t-1][te][0] > maxpos:
            lastchar = te
            maxpos = possen[t-1][te][0]
    
    result = deque()
    result.appendleft(lastchar)
    i = t - 1
    while i >= 0:
        l, j = lastchar, i
        lastchar, i = possen[j][l][2], possen[j][l][1]
        # i = possen[i][lastchar][1]
        result.appendleft(lastchar)
    
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
    for char in result:
        print(char, end=' ')
    print('')

    line = fin.readline()
