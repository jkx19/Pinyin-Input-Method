import json
import os
import re
from collections import defaultdict

# calculate the transform probability

# make the pin2cha dictionary
chin = open('../pinyintable/拼音汉字表.txt', 'r', encoding='gbk')
dictionary = defaultdict(set)

line = chin.readline()
while line != '':

    rl = re.split(' ', line.strip())
    # print(rl)

    pin = rl[0]
    for ch in rl[1:]:
        dictionary[pin].add(ch)

    line = chin.readline()
chin.close()

for pin in dictionary.keys():     
     dictionary[pin] = list(dictionary[pin])

pin2cha = open('../dict/pin2char.json', 'w')
json.dump(dictionary, pin2cha)
pin2cha.close()


# char to pin
dictionary.clear()
dictionary = defaultdict(set)

chin = open('../pinyintable/拼音汉字表.txt', 'r', encoding='gbk')

line = chin.readline()
while line != '':
    rl = re.split(' ', line.strip())
    # print(rl)

    pin = rl[0]
    for ch in rl[1:]:
        dictionary[ch].add(pin)

    line = chin.readline()
chin.close()

for char in dictionary.keys():     
     dictionary[char] = list(dictionary[char])

char2pin = open('../dict/char2pin.json', 'w')
json.dump(dictionary, char2pin)
char2pin.close()