import sys
import os

def get_result(args):
    from model.bi_gram import bi_gram
    from model.tri_gram import tri_gram
    from model.word_gram import word_gram

    inputf = 'input/input.txt'
    outputf = 'output/output.txt'
    model = ''

    inputf = args.input
    outputf = args.output
    model = args.model


    if model == 'bi':
        k = bi_gram()
    elif model == 'tri':
        k = tri_gram()
    elif model == 'word':
        k = word_gram()
    else:
        print('model not supported')
        sys.exit()

    k.get_result(inputf, outputf)

import argparse
parser = argparse.ArgumentParser(description='Run the pinyin input python scripts')
parser.add_argument('model',type=str, choices=['bi','tri','word'], help='choose from bi, tri and word')
parser.add_argument('--input',type=str, default='input.txt', help='choose an input file in input/')
parser.add_argument('--output',type=str, default='output.txt', help='choose an output file in output/')
args = parser.parse_args()
get_result(args)