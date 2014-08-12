#-------------------------------------------------------------------------------
# Name:        EmotionLexicon.py
#
# Purpose:     Interface for Hashtag Emotion Lexicon data
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys
import os
from collections import defaultdict



BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')


class EmotionLexicon:


    def __init__(self):

        # Store data
        self._data = defaultdict(lambda:('',0))


        # Files containing data
        filename = os.path.join(BASE_DIR,'lexicons/HashtagEmotion/hashtag-emotion-0.2.txt')


        # Populate table with positive words
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f.readlines()[38:]: # skip header
                    line = line.split()
                    self._data[line[1]] = ( line[0], float(line[2]) )
        else:
            print >>sys.stderr, 'ERROR: Unable to read lexicon: EmotionLexicon'


    def lookup(self, word):
        return self._data[word]

