import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation
import sys
import math
from pathlib import Path
import heapq

def mat_gen_3():
    sys.stdout = sys.__stdout__
    
    charlist = []
    charin = open('pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
    c = charin.read()
    charlist = list(c)
    charlist = charlist + ['b', 'e']
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
            if len(trma[ch1][ch2].keys()) == 0:
                trma[ch1].pop(ch2)
            else:
                for c in trma[ch1][ch2].keys():
                    trma[ch1][ch2][c] /= emg[ch1][ch2]

    trmaout = open(f'data/matrix_3.json', 'w')
    json.dump(trma, trmaout)
    trmaout.close

    eout = open(f'data/occur_3.json', 'w')
    json.dump(emg, eout)
    eout.close()

def trigram(inputf, outputf):

    sys.stdout = open('output/'+outputf, 'w')
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


    def probability3(la0, la1, cur) -> float:
        if occur2[la1] == 0:
            return math.log(beta)
        
        elif occur3[la0][la1] == 0:
            return math.log(beta + alpha*math.exp(probability2(la0, la1)))

        else:
            if cur not in matrix3[la0][la1].keys():
                p = 0
            else:
                p = matrix3[la0][la1][cur]
            return math.log(beta + alpha*math.exp(probability2(la0, la1)) + p)


    def probability2(w0, w1):
        if occur2[w0] == 0:
            p = beta + alpha*occur2[w1]
        else:
            if w1 not in matrix2[w0].keys():
                p = beta
            else:
                p = alpha*occur2[w1] + matrix2[w0][w1]
        return math.log(p)

    def convert_2(pinlist:list) -> list:
        t = len(pinlist)
        possen = []
        for p in dic[pinlist[0]]:
            possen.append({})
            pro = probability2('b', p)
            possen[0][p] = [pro, '']
        
        for i in range(1,t):
            possen.append({}) # possen[i] == {}
            for cur in dic[pinlist[i]]:
                pcur = -float('inf')
                las = ''
                for la in possen[i-1].keys():
                    pro = probability2(la,cur)
                    if possen[i-1][la][0] + pro > pcur:
                        pcur = possen[i-1][la][0] + pro
                        las = la
                possen[i][cur] = [pcur, las]

        lastchar = ''
        maxpos = float('-inf')
        for te in possen[t - 1].keys():
            pro = probability2(te,'e')
            if possen[t-1][te][0]+pro > maxpos:
                lastchar = te
                maxpos = possen[t-1][te][0]+pro
        
        result = [lastchar]
        for i in range(1,t):
            lastchar = possen[t-i][lastchar][1]
            result.append(lastchar)
        
        return result

    def gen_max_pro_list(pinlist:list, N: int) -> list:
        t = len(pinlist)
        possen = []
        for p in dic[pinlist[0]]:
            possen.append({})
            pro = probability2('b', p)
            possen[0][p] = [pro, '']
        
        for i in range(1,t):
            possen.append({}) # possen[i] == {}
            for cur in dic[pinlist[i]]:
                pcur = -float('inf')
                las = ''
                for la in possen[i-1].keys():
                    pro = probability2(la,cur)
                    if possen[i-1][la][0] + pro > pcur:
                        pcur = possen[i-1][la][0] + pro
                        las = la
                possen[i][cur] = [pcur, las]

        heap = []
        for te in possen[t - 1].keys():
            pro = probability2(te,'e') + possen[t-1][te][0]
            heapq.heappush(heap, (pro,te))
            if len(heap) > N:
                heapq.heappop(heap)
        
        result = []
        for i in range(len(pinlist)):
            result.append(set())

        for lastchar_tu in heap:
            lastchar = lastchar_tu[1]
            result[t-1].add(lastchar)
            for i in range(1,t):
                lastchar = possen[t-i][lastchar][1]
                result[t-i-1].add(lastchar)
        return result


    def convert_3(pinlist:list) -> list:

        charlist = gen_max_pro_list(pinlist, 10)
        # print(charlist)
        t = len(pinlist)
        possen = [{}]

        for w1 in charlist[0]:
            for w2 in charlist[1]:
                pcur = probability3('b',w1,w2) + probability2('b', 'w1')
                las = 'b' + w1
                possen[0][w1+w2] = [pcur, las]
            
        for i in range(2,len(pinlist)):
            possen.append({})
            for w1 in charlist[i-1]:
                for w2 in charlist[i]:
                    pcur = -float('inf')
                    las = ''
                    for w0 in charlist[i-2]:
                        p = probability3(w0,w1,w2)
                        if possen[i-2][w0+w1][0] + p > pcur:
                            pcur = possen[i-2][w0+w1][0] + p
                            las = w0 + w1
                    possen[i-1][w1+w2] = [pcur, las]
        possen.append({})
        for w1 in charlist[t-1]:
            pcur = float('-inf')
            las = ''
            for w0 in charlist[t-2]:
                p = probability3(w0,w1,'e') + possen[t-2][w0+w1][0]
                if p > pcur:
                    pcur = p
                    las = w0+w1
            possen[t-1][w1+'e'] = [pcur, las]

        # print(possen)

        lastchar = ''
        maxpos = float('-inf')
        for te in possen[t - 1].keys():
            if possen[t-1][te][0] > maxpos:
                lastchar = te
                maxpos = possen[t-1][te][0]
        
        result = [lastchar[0]]
        for i in range(1,t):
            lastchar = possen[t-i][lastchar][1]
            result.append(lastchar[0])
        
        return result



    fin = open('input/input.txt', 'r')
    line = fin.readline()
    k = 0
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
        k = k + 1


class tri_gram:
    
    def __init__(self) -> None:
        pass

    def gen_mat(self):
        mat_gen_3()

    def get_result(self, inputf, outputf):
        matf = Path('data/matrix_3.json')
        if not matf.is_file():
            self.gen_mat()
        trigram(inputf, outputf)