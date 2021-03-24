import heapq
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
from collections import deque

def gen_word():
    numwords = 12000
    w = 20
    sys.stdout = sys.__stdout__

    # 计算状态转移的概率，没有做拉普拉斯平滑，没有出现的字符的转出概率全部为0
    # 得到matrix.json，且matrix[i][j]表示P(j|i)
    # bi-gram

    charlist = []
    charin = open('pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
    c = charin.read()
    charlist = list(c)
    charset = set(charlist)
    charin.close()

    trma = defaultdict(dict)
    nma = defaultdict(dict)
    emg_b = {}
    emg_a = {}
    for ch in charlist:
        emg_b[ch] = 0
        emg_a[ch] = 0
        for cha in charlist:
            trma[ch][cha] = 0
            nma[ch][cha] = 0

    newsf = open('trainset/sina_news.txt', 'r')
    news = newsf.readline()
    k = 0
    while news != '':
        news = news.strip()
        for i in range(len(news) - 1):
            if news[i] in charset and news[i + 1] in charset:
                trma[news[i]][news[i+1]] += 1
                nma[news[i+1]][news[i]] += 1
                emg_b[news[i]] += 1
                emg_a[news[i+1]] += 1
        k = k + 1
        if k % 10000 == 0:
            print(f'processing the {k}th line')
        news = newsf.readline()
    newsf.close()


    wordlist = []

    np = []
    for ch in charlist:
        if emg_b[ch] == 0:
            print(ch)
            np.append(ch)

        else:
            for c in trma[ch].keys():
                trma[ch][c] /= emg_b[ch]

        if emg_a[ch] != 0:
            for c in nma[ch].keys():
                nma[ch][c] /= emg_a[ch]

    charnum = 0
    for ch in emg_a.keys():
        charnum += emg_a[ch]

    def value(c0, c1) -> float:
        thh = 5e-4*charnum
        p0, p1 = trma[c0][c1], nma[c1][c0]
        fr = math.log10(emg_b[c0]/charnum*emg_a[c1]/charnum + math.pow(0.1, w))
        weight = -(-w-fr)/w
        if emg_b[c0] < thh and emg_a[c1] < thh:
            return 0
        else:
            return p0*p1*weight

    for c0 in charlist:
        for c1 in charlist:
            p = value(c0, c1)
            if wordlist == []:
                wordlist.append((p,c0,c1))
            elif p > wordlist[0][0]:
                heapq.heappush(wordlist, (p,c0,c1))
                if len(wordlist) > numwords:
                    heapq.heappop(wordlist)

    outf = open('data/word/wordlist.json', 'w')
    dictin = open('data/char2pin.json', 'r')
    char2pin = json.load(dictin)
    dictin.close()
    out = defaultdict(set)
    for tu in wordlist:
        c0 = tu[1]
        c1 = tu[2]
        for p0 in char2pin[c0]:
            for p1 in char2pin[c1]:
                out[p0 + ' ' + p1].add(c0 + c1)

    for py in out.keys():
        out[py] = list(out[py])

    json.dump(out, outf)
    outf.close

def mat_gen_word():
    # 计算状态转移的概率，没有做拉普拉斯平滑，没有出现的字符的转出概率全部为0
    # 得到matrix.json，且matrix[i][j]表示P(j|i)
    # bi-gram
    # 增加了开始标识'b'以及结束标识'e'

    sys.stdout = sys.__stdout__

    charlist = []
    charin = open('pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
    c = charin.read()
    charlist = list(c)
    charset = set(charlist)
    charin.close()

    charset.add('b') # begin token
    charset.add('e') # end token
    charlist.append('b')
    charlist.append('e')

    wordlistin = open('data/word/wordlist.json', 'r')
    worddict = json.load(wordlistin)
    wordlistin.close()
    wordset = set()
    for wl in worddict.values():
        for w in wl:
            wordset.add(w)
    wordlist = list(wordset)
    trma = defaultdict(dict)
    emg = {}
    for ch in charlist + wordlist:
        emg[ch] = 0

    newsf = open('trainset/sina_news.txt', 'r')
    news = newsf.readline()
    k = 0
    while news != '':
        news = news.strip()
        news = 'b' + news + 'e'        
        i = 0
        while i < len(news) - 1:
            if news[i]+news[i+1] in wordset:
                if i < len(news) - 3 and news[i+2]+news[i+3] in wordset:
                    if news[i+2]+news[i+3] not in trma[news[i]+news[i+1]].keys():
                        trma[news[i]+news[i+1]][news[i+2]+news[i+3]] = 0
                    trma[news[i]+news[i+1]][news[i+2]+news[i+3]] += 1
                    emg[news[i]+news[i+1]] += 1
                elif i < len(news)-2 and news[i+2] in charset:
                    if news[i+2] not in trma[news[i]+news[i+1]].keys():
                        trma[news[i]+news[i+1]][news[i+2]] = 0
                    trma[news[i]+news[i+1]][news[i+2]] += 1
                    emg[news[i]+news[i+1]] += 1
                i += 2
            
            elif i< len(news)-2 and news[i] in charset:
                if i < len(news)-2 and news[i+1]+news[i+2] in wordset:
                    if news[i+1]+news[i+2] not in trma[news[i]].keys():
                        trma[news[i]][news[i+1]+news[i+2]] = 0
                    trma[news[i]][news[i+1]+news[i+2]] += 1
                    emg[news[i]] += 1
                elif news[i+1] in charset:
                    if news[i+1] not in trma[news[i]].keys():
                        trma[news[i]][news[i+1]] = 0
                    trma[news[i]][news[i+1]] += 1
                    emg[news[i]] += 1
                i += 1
            else:
                i += 1

        k = k + 1
        if k % 10000 == 0:
            print(f'processing the {k}th line')
        news = newsf.readline()
    newsf.close()

    np = []
    for ch in charlist + wordlist:
        if emg[ch] == 0:
            print(ch)
            np.append(ch)
        else:
            for c in trma[ch].keys():
                trma[ch][c] /= emg[ch]

    trmaout = open('data/word/matrix_w.json', 'w')
    json.dump(trma, trmaout)
    trmaout.close

    eout = open('data/word/occur.json', 'w')
    json.dump(emg, eout)
    eout.close()

def wordgram(inputf, outputf):
    # Basic bi-gram model with viterbi algorithm
    # Considering common words in news
    # b, e stand for begin and end.
    sys.stdout = open('output/'+outputf, 'w')

    mat_in = open('data/word/matrix_w.json', 'r')
    matrix = json.load(mat_in)
    mat_in.close()

    dictf = open('data/pin2char.json', 'r')
    p2c = json.load(dictf)
    dictf.close()

    occf = open('data/word/occur.json', 'r')
    occur = json.load(occf)
    occf.close()

    wordf = open('data/word/wordlist.json', 'r')
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

    def probability(w0, w1):
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
                        possen[1][word] = [probability('b', word), -1, 'b']
                for ch in p2c[pinlist[0]]:
                    possen[0][ch] = [probability('b', ch), -1, 'b']

            else:
                if i < t-1:
                    if pinlist[i]+' '+pinlist[i+1] in wordset:
                        for word in p2w[pinlist[i]+' '+pinlist[i+1]]:
                            pcur = -float('inf')
                            las = ''
                            for la in possen[i-1].keys():
                                p = probability(la,word)
                                if possen[i-1][la][0] + p> pcur:
                                    pcur = possen[i-1][la][0] + p
                                    las = la
                            possen[i+1][word] = [pcur, i-1, las]
            
                for cur in p2c[pinlist[i]]:
                    pcur = -float('inf')
                    las = ''
                    for la in possen[i-1].keys():
                        p = probability(la, cur)
                        if possen[i-1][la][0] + p > pcur:
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
            result.appendleft(lastchar)
        
        result.popleft() # pop the 'b' token
        return result

    # laplacian(matrix)
    fin = open('input/'+inputf, 'r')
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
    

class word_gram:
    
    def __init__(self) -> None:
        wordlistf = Path('data/word/wordlist.json')
        if not wordlistf.is_file():
            gen_word()

    def gen_mat(self):
        mat_gen_word()

    def get_result(self, inputf, outputf):
        matf = Path('data/word/matrix_w.json')
        if not matf.is_file():
            self.gen_mat()
        wordgram(inputf, outputf)