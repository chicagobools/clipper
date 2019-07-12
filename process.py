# -*- coding: utf-8 -*-
import fileinput
import string
import sys
import os
from os import path
import random
from collections import defaultdict
from itertools import groupby
import io
import json

def stripPunct(line):
    return ' '.join(filter(None, (word.strip(string.punctuation) for word in line.split())))

def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def gen_grams(iterable):
    return [find_ngrams(iterable, i) for i in range(1,4)]

def movie_words(folder, fileNames):
    '''
        reads SRT files into a dictionary of dictionaries containing time stamps
        of ngram occurrences to read at a later date when matching with song lyrics
        { ngram: {movie : timestamp, ...}, ...}
    '''
    movie = defaultdict(lambda: defaultdict(list))
    #this here parses the srt files and splits each file into groups of dialogue
    for filename in fileNames:
        try:
            with io.open(path.relpath(folder+filename), 'r', encoding='utf-8-sig') as f:
                subs = [list(g) for b, g in groupby(f, lambda x: bool(x.strip())) if b]
        except UnicodeDecodeError:
            pass
        # at this point the above contains a list of lists, where each inner list is a dialogue group
        # iterate through unigram, bigram, trigram and start indexing them in a dictionary by movie
        # {ngram : {movie: timestamp, ... }, ... } 
        for group in subs:
            for dialogue in group[2:]:
                dialogue_format = dialogue.rstrip().lower()
                indiv_words = stripPunct(dialogue_format).split()
                ngrams = gen_grams(indiv_words)
                for grams in ngrams:
                    #shuffle list of grams to keep diversity
                    random.shuffle(grams)
                    for each_gram in grams:
                        if len(movie[each_gram][filename]) < 21:
                            movie[each_gram][filename].append(group[1].rstrip())
    return movie

def write_file(dictionary):
    file = open('dialogue_grams.txt', 'w')
    for word in dictionary:
        for movie in dictionary[word]:
            for instance in dictionary[word][movie]:
                file.write("[%s, '%s', '%s']\n" % (word, movie, instance))

def main():
    folder = str(sys.argv[1])+"/"
    files = [f for f in os.listdir(path.relpath(folder)) if f.endswith('.srt')]
    test = movie_words(folder, files)
    write_file(test)

main()
