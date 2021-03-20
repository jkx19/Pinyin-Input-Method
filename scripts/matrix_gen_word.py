import os
import json
import re
import string
from collections import defaultdict
from zhon.hanzi import punctuation

# 计算状态转移的概率，没有做拉普拉斯平滑，没有出现的字符的转出概率全部为0
# 得到matrix.json，且matrix[i][j]表示P(j|i)
# bi-gram
# 增加了开始标识'b'以及结束标识'e'

charlist = []
charin = open('../pinyintable/一二级汉字表.txt', 'r', encoding='gbk')
c = charin.read()
charlist = list(c)
charset = set(charlist)
charin.close()

charset.add('b') # begin token
charset.add('e') # end token
charlist.append('b')
charlist.append('e')

wordlistin = open('../data/word/wordlist.json', 'r')
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
    # for cha in charlist + wordlist:
    #     trma[ch][cha] = 0

# the following part is specific for sina news
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
#             # for i in range(len(news) - 1):
#             #     if news[i] in charset and news[i + 1] in charset:
#             #         trma[news[i]][news[i+1]] += 1
#             #         emg[news[i]] += 1
#             news = 'b' + news + 'e'

#             i = 0
#             while i < len(news) - 1:
#                 if news[i]+news[i+1] in wordset:
#                     if i < len(news) - 3 and news[i+2]+news[i+3] in wordset:
#                         if news[i+2]+news[i+3] not in trma[news[i]+news[i+1]].keys():
#                             trma[news[i]+news[i+1]][news[i+2]+news[i+3]] = 0
#                         trma[news[i]+news[i+1]][news[i+2]+news[i+3]] += 1
#                         emg[news[i]+news[i+1]] += 1
#                     elif i < len(news)-2 and news[i+2] in charset:
#                         if news[i+2] not in trma[news[i]+news[i+1]].keys():
#                             trma[news[i]+news[i+1]][news[i+2]] = 0
#                         trma[news[i]+news[i+1]][news[i+2]] += 1
#                         emg[news[i]+news[i+1]] += 1
#                     i += 2
                
#                 elif i< len(news)-2 and news[i] in charset:
#                     if i < len(news)-2 and news[i+1]+news[i+2] in wordset:
#                         if news[i+1]+news[i+2] not in trma[news[i]].keys():
#                             trma[news[i]][news[i+1]+news[i+2]] = 0
#                         trma[news[i]][news[i+1]+news[i+2]] += 1
#                         emg[news[i]] += 1
#                     elif news[i+1] in charset:
#                         if news[i+1] not in trma[news[i]].keys():
#                             trma[news[i]][news[i+1]] = 0
#                         trma[news[i]][news[i+1]] += 1
#                         emg[news[i]] += 1
#                     i += 1
#                 else:
#                     i += 1


#         k = k + 1
#         if k % 100 == 0:
#             print(f'processing the {k}th news of 2016-{month}')
#         newsline = newsf.readline()
#     newsf.close()



newsf = open('../trainset/sina_news.txt', 'r')
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

trmaout = open('../data/word/matrix_w.json', 'w')
json.dump(trma, trmaout)
trmaout.close

eout = open('../data/word/occur.json', 'w')
json.dump(emg, eout)
eout.close()

# if np != []:
#     noout = open('../data/not_in_news.json', 'w')
#     json.dump(np, noout)
#     noout.close()