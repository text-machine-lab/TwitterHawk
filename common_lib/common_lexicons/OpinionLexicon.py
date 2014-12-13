#-------------------------------------------------------------------------------
# Name:        OpinionLexicon.py
#
# Purpose:     Interface for OpinionLexiocn data
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys
import os


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules



class OpinionLexicon:


    def __init__(self):

        # Store data
        self._pos = set([])
        self._neg = set([])


        # Files containing data
        base_dir = enabled_modules['lexicons']
        pos_f = os.path.join(base_dir,'OpinionLexicon/positive-words.txt')
        neg_f = os.path.join(base_dir,'OpinionLexicon/negative-words.txt')


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
