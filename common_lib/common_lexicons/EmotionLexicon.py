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


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules



class EmotionLexicon:


    def __init__(self):

        # Store data
        self._data = defaultdict(lambda:('',0))


        # Files containing data
        base_dir = enabled_modules['lexicons']
        filename = os.path.join(base_dir,'HashtagEmotion/hashtag-emotion-0.2.txt')


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

