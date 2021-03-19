import os
import re
import json
import sys
import math
from collections import deque

# Basic bi-gram model with viterbi algorithm
# Considering common words in news
# b, e stand for begin and end.

sys.stdout = open('../output/output.txt', 'w')

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

alpha = 1e-30
beta = 1e-70

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

def probability(w0, w1):
    # if occur[w0] == 0:
    #     return math.log(alpha)
    # else:
    #     for cur in matrix[la].keys():
    #         if matrix[la][cur] == 0:
    #             matrix[la][cur] = math.log(alpha*(occur[cur]+alpha))
    #         else:
    #             matrix[la][cur] = math.log(alpha*occur[cur] + (1-alpha)*matrix[la][cur])
    if occur[w0] == 0:
        p = beta + alpha*occur[w1]
    else:
        if w1 not in matrix[w0].keys():
            p = beta
        else:
            p = alpha*occur[w1] + matrix[w0][w1]
    return math.log(p)



# Laplacian smoothing
def convert(pinlist:list) -> deque:

    t = len(pinlist)
    possen = []
    for i in range(t):
        possen.append({})

    i = 0
    while i < t:
        if i == 0:
            if i < t-1 and pinlist[0]+' '+pinlist[1] in wordset:
                for word in p2w[pinlist[0]+' '+pinlist[1]]:
                    # possen[1][word] = (matrix['b'][word], -1, 'b')
                    possen[1][word] = [probability('b', word), -1, 'b']
            for ch in p2c[pinlist[0]]:
                # possen[0][ch] = [matrix['e'][ch], -1, 'b']
                possen[0][ch] = [probability('b', ch), -1, 'b']

        else:
            if i < t-1:
                if pinlist[i]+' '+pinlist[i+1] in wordset:
                    for word in p2w[pinlist[i]+' '+pinlist[i+1]]:
                        pcur = -float('inf')
                        las = ''
                        for la in possen[i-1].keys():
                            p = probability(la,word)
                            # if possen[i-1][la][0] + matrix[la][word] > pcur:
                            if possen[i-1][la][0] + p> pcur:
                                pcur = possen[i-1][la][0] + p
                                las = la
                        possen[i+1][word] = [pcur, i-1, las]
        
            for cur in p2c[pinlist[i]]:
                pcur = -float('inf')
                las = ''
                for la in possen[i-1].keys():
                    p = probability(la, cur)
                    # if possen[i-1][la][0] + matrix[la][cur] > pcur:
                    if possen[i-1][la][0] + p > pcur:
                        # pcur = possen[i-1][la][0] + matrix[la][cur]
                        pcur = possen[i-1][la][0] + p
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
    
    result.popleft() # pop the 'b' token
    return result

# laplacian(matrix)
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
        print(char, end='')
    print('')

    line = fin.readline()
