import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation
import sys
import math
from pathlib import Path

def mat_gen_3():
    # n = 3
    charlist = []
    charin = open('pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
    c = charin.read()
    charlist = list(c)
    charset = set(charlist)
    charin.close()

    trma = defaultdict(dict)
    emg = defaultdict(dict)
    for ch1 in charlist:
        for ch2 in charlist:
            emg[ch1][ch2] = 0
            trma[ch1][ch2] = {}


    newsf = open('trainset/sina_news.txt', 'r')
    news = newsf.readline()
    k = 0
    while news != '':
        news = news.strip()
        
        for i in range(len(news) - 2):
            if news[i] in charset and news[i + 1] in charset and news[i + 2] in charset:
                if news[i+2] not in trma[news[i]][news[i+1]].keys():
                    trma[news[i]][news[i+1]][news[i+2]] = 0
                trma[news[i]][news[i+1]][news[i+2]] += 1
                emg[news[i]][news[i+1]] += 1

        k = k + 1
        if k % 10000 == 0:
            print(f'processing the {k}th line')
        news = newsf.readline()
    newsf.close()




    for ch1 in charlist:
        for ch2 in charlist:
            for c in trma[ch1][ch2].keys():
                trma[ch1][ch2][c] /= emg[ch1][ch2]

    trmaout = open(f'data/matrix_3.json', 'w')
    json.dump(trma, trmaout)
    trmaout.close

    eout = open(f'data/occur_3.json', 'w')
    json.dump(emg, eout)
    eout.close()

def trigram():
    mat2_in = open('data/matrix.json', 'r')
    matrix2 = json.load(mat2_in)
    mat2_in.close()

    mat3_in =open('data/matrix_3.json', 'r')
    matrix3 = json.load(mat3_in)
    mat3_in.close()

    dictf = open('data/pin2char.json', 'r')
    dic = json.load(dictf)
    dictf.close()

    occf2 = open('data/occur.json', 'r')
    occur2 = json.load(occf2)
    occf2.close()

    occf3 = open('data/occur_3.json', 'r')
    occur3 = json.load(occf3)
    occf3.close()

    alpha = 1e-20
    beta = 1e-45

    def laplacian(matrix:dict):
        for la in matrix.keys():
            if occur2[la] == 0:
                for cur in matrix[la].keys():
                    matrix[la][cur] = math.log(alpha)
            else:
                for cur in matrix[la].keys():
                    if matrix[la][cur] == 0:
                        matrix[la][cur] = math.log(alpha*(occur2[cur]+alpha))
                    else:
                        matrix[la][cur] = math.log(alpha*occur2[cur] + (1-alpha)*matrix[la][cur])


    def laplacian3(la0, la1, cur) -> float:
        if occur2[la1] == 0:
            return math.log(beta)
        
        elif occur3[la0][la1] == 0:
            return math.log(beta + alpha*matrix2[la1][cur])

        else:
            if cur not in matrix3[la0][la1].keys():
                p = 0
            else:
                p = matrix3[la0][la1][cur]
            return math.log(beta + alpha*matrix2[la1][cur] + p)


    def convert_2(pinlist:list) -> list:
        t = len(pinlist)
        possen = []
        for p in dic[pinlist[0]]:
            possen.append({})
            possen[0][p] = [math.log(occur2[p] + alpha), '']
        
        for i in range(1,t):
            possen.append({}) # possen[i] == {}
            for cur in dic[pinlist[i]]:
                pcur = -float('inf')
                las0 = ''
                las1 = ''
                for la in possen[i-1].keys():
                    if possen[i-1][la][0] + matrix2[la][cur] > pcur:
                        pcur = possen[i-1][la][0] + matrix2[la][cur]
                        las1 = la
                        las0 = possen[i-1][las1][1]
                possen[i][cur] = [pcur, las1]
                possen[i-1][las1][1] = las0

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


    def convert_3(pinlist:list) -> list:
        t = len(pinlist)
        possen = []
        for p in dic[pinlist[0]]:
            possen.append({})
            possen[0][p] = [math.log(occur2[p] + alpha), '']

        for p in dic[pinlist[1]]:
            possen.append({})
            pcur = -float('inf')
            las = ''
            for la in possen[0].keys():
                if possen[0][la][0] + math.log(matrix2[la][p] + alpha) > pcur:
                    pcur = possen[0][la][0] + math.log(matrix2[la][p] + alpha)
                    las = la
            possen[1][p] = [pcur, las]

        
        for i in range(2,t):
            possen.append({}) # possen[i] == {}
            for cur in dic[pinlist[i]]:
                pcur = -float('inf')
                las0 = ''
                las1 = ''
                for la0 in possen[i-2].keys():
                    for la1 in possen[i-1].keys():
                        probability = laplacian3(la0, la1, cur)
                        prob = probability + possen[i-1][la1][0] + possen[i-2][la0][0]
                        if prob > pcur:
                            pcur = prob
                            las1 = la1
                            las0 = la0
                possen[i][cur] = [pcur, las1]
                # possen[i-1][las1][1] = las0

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



    fin = open('input/input.txt', 'r')
    line = fin.readline()
    while line != '':
        pinlist = re.split(' ', line.strip())
        length = len(pinlist)
        for p in pinlist:
            print(p, end=' ')
        print('')
        if length <= 2:
            result = convert_2(pinlist)
        else:
            result = convert_3(pinlist)
        for i in range(length):
            print(result[length - 1 - i], end='')
        print('')

        line = fin.readline()

class tri_gram:
    
    def __init__(self) -> None:
        pass

    def gen_mat(self):
        mat_gen_3()

    def get_result(self):
        matf = Path('data/matrix_3.json')
        if not matf.is_file():
            # self.gen_mat()
            print('no')
        else:
            pass
            # print('yes')
        trigram()