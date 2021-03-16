import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation

# 计算状态转移的概率，没有做拉普拉斯平滑，没有出现的字符组的转出概率全部为0
# 得到matrix.json，且matrix[i][j][k]表示P(k|i,j), 但是第三项使用了邻接表的储存方式，因此无法索引没有的
# n-gram

n = 3

charlist = []
charin = open('../pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
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
        # for ch3 in charlist:
        #     trma[ch1][ch2][ch3] = 0   Memory extensive

months = ['02','04','05','06','07','08','09','10','11']
for month in months:
    newsf = open(f'../sina_news_gbk/2016-{month}.txt', 'r', encoding='gbk')
    newsline = newsf.readline()
    print(f'processing news in 2016-{month}')
    k = 0
    while newsline != '':
        newsj = json.loads(newsline.strip())
        newst = newsj['html'] + '，' + newsj['title']
        newst = re.sub('[0-9]+|[a-z]+|[A-Z]+|\s+', '，', newst)
        newsl = re.split('[%s%s]+' %(punctuation,string.punctuation), newst)
        
        for news in newsl:
            for i in range(len(news) - n + 1):
                if news[i] in charset and news[i + 1] in charset and news[i + 2] in charset:
                    if news[i+2] not in trma[news[i]][news[i+1]].keys():
                        trma[news[i]][news[i+1]][news[i+2]] = 0
                    trma[news[i]][news[i+1]][news[i+2]] += 1
                    emg[news[i]][news[i+1]] += 1

        k = k + 1
        if k % 1000 == 0:
            print(f'processing the {k}th news of 2016-{month}')
        newsline = newsf.readline()
    newsf.close()

# np = []
for ch1 in charlist:
    for ch2 in charlist:
        # if emg[ch1][ch2] == 0:
        #     print(ch)
        #     np.append(ch)

        for c in trma[ch1][ch2].keys():
            trma[ch1][ch2][c] /= emg[ch1][ch2]

trmaout = open(f'../data/matrix_{n}.json', 'w')
json.dump(trma, trmaout)
trmaout.close

eout = open(f'../data/occur_{n}.json', 'w')
json.dump(emg, eout)
eout.close()

# if np != []:
#     noout = open('../data/not_in_news.json', 'w')
#     json.dump(np, noout)
#     noout.close()