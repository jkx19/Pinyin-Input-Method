import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation

import sys
import math
from pathlib import Path
# sys.stdout = open('../output/output.txt', 'w')

def mat_gen_2():
    sys.stdout = sys.__stdout__

    charlist = []
    charin = open('../pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
    c = charin.read()
    charlist = list(c)
    charset = set(charlist)
    charin.close()

    trma = defaultdict(dict)
    emg = {}
    for ch in charlist:
        emg[ch] = 0
        for cha in charlist:
            trma[ch][cha] = 0

    newsf = open('../trainset/sina_news.txt', 'r')
    news = newsf.readline()
    k = 0
    while news != '':
        news = news.strip()
        for i in range(len(news) - 1):
            if news[i] in charset and news[i + 1] in charset:
                trma[news[i]][news[i+1]] += 1
                emg[news[i]] += 1

        k = k + 1
        if k % 10000 == 0:
            print(f'processing the {k}th line')
        news = newsf.readline()
    newsf.close()


    np = []
    for ch in charlist:
        if emg[ch] == 0:
            print(ch)
            np.append(ch)

        else:
            for c in trma[ch].keys():
                trma[ch][c] /= emg[ch]

    trmaout = open('../data/matrix.json', 'w')
    json.dump(trma, trmaout)
    trmaout.close

    eout = open('../data/occur.json', 'w')
    json.dump(emg, eout)
    eout.close()

def bigram(inputf, outputf):
    sys.stdout = open('output/'+outputf, 'w')
    mat_in = open('data/matrix.json', 'r')
    matrix = json.load(mat_in)
    mat_in.close()

    dictf = open('data/pin2char.json', 'r')
    dic = json.load(dictf)
    dictf.close()

    occf = open('data/occur.json', 'r')
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
    fin = open('input/'+inputf, 'r')
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

class bi_gram:
    
    def __init__(self) -> None:
        pass

    def gen_mat(self):
        mat_gen_2()

    def get_result(self, inputf, outputf):
        matf = Path('data/matrix.json')
        if not matf.is_file():
            self.gen_mat()
        bigram(inputf, outputf)
        
