import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation

# 计算状态转移的概率，没有做拉普拉斯平滑，没有出现的字符的转出概率全部为0
# 得到matrix.json，且matrix[i][j]表示P(j|i)
# bi-gram

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

eout = open('../data/occur_d.json', 'w')
json.dump(emg, eout)
eout.close()

if np != []:
    noout = open('../data/not_in_news.json', 'w')
    json.dump(np, noout)
    noout.close()