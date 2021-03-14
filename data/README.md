# Data

## char2pin.json

This is a dict that provide index for character to a list of pinyin

## pin2char.json

A dict with keys composed by pinyin and values a list of characters

## not_in_news.json

Characters not in the training dataset

## matrix.json

A two-layer dict indexed by characters. matrix[last][current] stands for P(current | last). If 'last' not in the dataset, all the value corresponding to it will be 0

## occur.json

A dict, with keys of characters and values the number of its key's occurence in the dataset
