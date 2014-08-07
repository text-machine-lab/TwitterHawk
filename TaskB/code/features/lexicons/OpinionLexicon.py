#-------------------------------------------------------------------------------
# Name:        OpinionLexicon.py
# Purpose:     Interface for OpinionLexiocn data
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys
import os



BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')


class OpinionLexicon:


    def __init__(self):

        # Store data
        self._pos = set([])
        self._neg = set([])


        # Files containing data
        pos_f = os.path.join(BASE_DIR,'lexicons/OpinionLexicon/positive-words.txt')
        neg_f = os.path.join(BASE_DIR,'lexicons/OpinionLexicon/negative-words.txt')


        # Populate table with positive words
        if os.path.exists(pos_f):
            with open(pos_f, 'r') as f:
                for line in f.readlines()[35:]: # skip header
                    self._pos.add(line.strip())
        else:
            print >>sys.stderr, 'ERROR: Unable to read positive lexicon: ', 'OpinionLexicon'


        # Populate table with positive words
        if os.path.exists(neg_f):
            with open(neg_f, 'r') as f:
                for line in f.readlines()[35:]: # skip header
                    self._neg.add(line.strip())
        else:
            print >>sys.stderr, 'ERROR: Unable to read negative lexicon: ', 'OpinionLexicon'



    def lookup(self, word):
        if word in self._pos: return 'positive'
        if word in self._neg: return 'negative'
        return 'neutral'
