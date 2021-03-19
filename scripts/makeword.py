import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation
import heapq
import math
import sys

numwords = 10000
w = 8

# numwords = int(sys.argv[1])
# w = int(sys.argv[2])
# print(sys.argv)

# 计算状态转移的概率，没有做拉普拉斯平滑，没有出现的字符的转出概率全部为0
# 得到matrix.json，且matrix[i][j]表示P(j|i)
# bi-gram

charlist = []
charin = open('../pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
c = charin.read()
charlist = list(c)
charset = set(charlist)
charin.close()

# trma = defaultdict(dict)
# nma = defaultdict(dict)
# emg_b = {}
# emg_a = {}
# for ch in charlist:
#     emg_b[ch] = 0
#     emg_a[ch] = 0
#     for cha in charlist:
#         trma[ch][cha] = 0
#         nma[ch][cha] = 0

# # the following part is specific for sina news
# months = ['02','04','05','06','07','08','09','10','11']
# for month in months:
#     newsf = open(f'../sina_news_gbk/2016-{month}.txt', 'r', encoding='gbk')
#     newsline = newsf.readline()
#     print(f'processing news in 2016-{month}')
#     k = 0
#     while newsline != '':
#         newsj = json.loads(newsline.strip())
#         newst = newsj['html'] + '，' + newsj['title']
#         newst = re.sub('[0-9]+|[a-z]+|[A-Z]+|\s+', '，', newst)
#         newsl = re.split('[%s%s]+' %(punctuation,string.punctuation), newst)
        
#         for news in newsl:
#             for i in range(len(news) - 1):
#                 if news[i] in charset and news[i + 1] in charset:
#                     trma[news[i]][news[i+1]] += 1
#                     nma[news[i+1]][news[i]] += 1
#                     emg_b[news[i]] += 1
#                     emg_a[news[i+1]] += 1

#         k = k + 1
#         if k % 1000 == 0:
#             print(f'processing the {k}th news of 2016-{month}')
#         newsline = newsf.readline()
#     newsf.close()

wordlist = []

# np = []
# for ch in charlist:
#     if emg_b[ch] == 0:
#         print(ch)
#         np.append(ch)

#     else:
#         for c in trma[ch].keys():
#             trma[ch][c] /= emg_b[ch]

#     if emg_a[ch] != 0:
#         for c in nma[ch].keys():
#             nma[ch][c] /= emg_a[ch]

trmaf = open('../data/word/matrix.json', 'r')
trma = json.load(trmaf)
trmaf.close()

nmaf = open('../data/word/rematrix.json', 'r')
nma = json.load(nmaf)
nmaf.close()

ebin = open('../data/occur.json', 'r')
emg_b = json.load(ebin)
ebin.close()

eain = open('../data/reoccur.json', 'r')
emg_a = json.load(eain)
eain.close()

charnum = 0
for ch in emg_a.keys():
    charnum += emg_a[ch]

def value(c0, c1) -> float:
    thh = 5e-4*charnum
    p0, p1 = trma[c0][c1], nma[c1][c0]
    fr = math.log(emg_b[c0]/charnum*emg_a[c1]/charnum + 1e-20)
    weight = (w-fr)/w
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

outf = open('../data/word/wordlist.json', 'w')
dictin = open('../data/char2pin.json', 'r')
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




# trmaout = open('../data/word/matrix.json', 'w')
# json.dump(trma, trmaout)
# trmaout.close

# nmaout = open('../data/word/rematrix.json', 'w')
# json.dump(nma, nmaout)
# nmaout.close

# eout = open('../data/occur.json', 'w')
# json.dump(emg_b, eout)
# eout.close()

# aout = open('../data/reoccur.json', 'w')
# json.dump(emg_a, aout)
# aout.close()

# if np != []:
#     noout = open('../data/not_in_news.json', 'w')
#     json.dump(np, noout)
#     noout.close()