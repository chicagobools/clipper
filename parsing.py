import fileinput
import itertools
import string
import sys
import os
from os import path
from collections import defaultdict
import random
import ast
import copy
from more_itertools import unique_everseen
from clips import search_clips

def stripPunct(line):
    return ' '.join(filter(None, (word.strip(string.punctuation) for word in line.split())))

def find_ngrams(input_list, n):
  return zip(*[input_list[i:] for i in range(n)])

def gen_grams(iterable):
    return [find_ngrams(iterable, i) for i in range(1,4)]

def removeNUL(string):
    return string.replace('\x00', '')

def randIndex(num):
    return random.randint(0, num-1)

def contained(obj, iterable):
    for i in iterable:
        if len(set(obj) & set(i)) > 0:
            return True
    return False
    #return any(len(set(obj) & set(i)) > 0 for i in iterable) 

def song_words(fileName):
    '''    
        splits each line of lyrics into ngrams and orders them in a list
        of lists in ascending order [ [unigram], [bigrams], [trigrams] ]
        but adds a tempvar to make the list zippable (transpose matrix) 
        in later functions
    '''
    grams = lambda str: gen_grams(stripPunct(str.lower().rstrip()).split())
    return [[i for i in [ngram for ngram in grams(line)]] for line in fileinput.input(fileName)]
    # li = list()
    # for line in fileinput.input(fileName):
    #     line = stripPunct(line.lower().rstrip() + ' temp_var'*2).split()
    #     line = [(line[i], i) for i in range(len(line))]
    #     li.append(zip(*gen_grams(line)))
    # return li



def song_grams(fileName):
    '''
        split each line of lyrics into ngrams and join them as an extended list
        return the list of extended lists as one whole extended list set
    '''
    grams = lambda str: gen_grams(stripPunct(str.lower()).split())
    # return list(itertools.chain(*[list(itertools.chain(*grams(line))) for line in fileinput.input(fileName)]))
    return list(itertools.chain([list(itertools.chain(grams(line))) for line in fileinput.input(fileName)]))

def group_lyrics(lyrics):
    with open(lyrics, 'r') as f:
        for line in f:
            words = stripPunct(line.lower()).split()
            length = len(line.split())
            nums = []

            while sum(nums) < length:
                if length - sum(nums) < 4:
                    nums.append(length - sum(nums))
                else:
                    nums.append(random.randint(1,3))

            index = 0
            for number in nums:
                yield words[index:index+number]
                index += number


def main():
    song_title = sys.argv[1]

    split_lyrics = group_lyrics(song_title)
  

    for count, group in enumerate(split_lyrics):
        name = str(count) + ' ' + ' '.join(group)
        search_clips(' '.join(group), name, 5)

    #table = defaultdict(list)
    #song = song_grams(song_title)




    # with open('dialogue_grams.txt') as f:
    #     for line in f:
    #         data = ast.literal_eval(line)
    #         ngram = data[0]
    #         table[ngram].append(data[1:])
    
    # song_set = song_words(song_title)

    # transpose_song_set = [list(j) for j in [itertools.izip_longest(*i[::-1]) for i in song_set]]

    # final = list()
    # for elm in song_set:
    #     in_order = []
    #     for i in elm:
    #         for j in i[::-1]:
    #             if zip(*j)[0] in table and not contained(j, in_order):
    #                 in_order.append(j)
    #     final.extend([zip(*i)[0] for i in list(unique_everseen(copy.deepcopy(in_order)))])
    #     #in_order[:] = []

    # for i in final:
    #     random.shuffle(table[i])
    #     if len(i) > 0:
    #         repeated = set()
    #         for j in range(5):
    #             index = randIndex(len(table[i]))
    #             if table[i][index][1] not in repeated:
    #                 print [map(str.upper,i), table[i][index]]
    #                 repeated.add(table[i][index][1])

main()