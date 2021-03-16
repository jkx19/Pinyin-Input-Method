import requests
import os
from collections import deque
from bs4 import BeautifulSoup
import re
import string
from zhon.hanzi import punctuation

urlset = set()
urlqueue = deque()
out = open('../trainset/baidubaike.txt', 'w')

header={

    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.5.2.18321'
#    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
}

def is_ch(c) -> bool:
    if '\u4e00' <= c <= '\u9fff':
            return True
    return False

i = 0

# url = 'https://baike.baidu.com/item/Python/407313?fr=aladdin'
url = '/item/Python/407313?fr=aladdin'
urlqueue.append(url)
while i < 10000:
    url_op = 'https://baike.baidu.com' + urlqueue.popleft()

    result = requests.get(url=url_op,headers=header)
    result.encoding = 'utf-8'
    html = result.text

    newurl = re.findall('href="(/item/.*?)"', html)
    for url in newurl:
        if url not in urlset:
            urlset.add(url)
            urlqueue.append(url)

    textblocks = re.sub('[0-9]+|[a-z]+|[A-Z]+|\s+|[\\/=<>]+', '，', html)
    #print(textblocks)
    textblocks = re.split('[%s%s]+' %(punctuation,string.punctuation), textblocks)[150:-1000]
    for tb in textblocks:
        for c in tb:
            if is_ch(c):
                out.write(c)
        out.write('\n')
    i = i + 1
    if i % 10 == 0:
        print(f'processing the {i}th website')
