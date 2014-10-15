#-------------------------------------------------------------------------------
# Name:        SubjectivityLexicon.py
#
# Purpose:     Interface for SubjectivityClues data
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


from collections import defaultdict
import os
import sys
import re



BASE_DIR = os.getenv('BISCUIT_DIR')


# Organize Data
class SubjectivityTuple:
    def __init__(self, t, pos, s, prior):
        self.type    = t
        self.pos     = pos
        self.stemmed = s
        self.prior   = prior

    def __str__(self):
        return self.type + '  ' + self.pos + '  ' + self.stemmed + '  ' + self.prior



class SubjectivityLexicon:

    def __init__(self):

        # Store data
        self._data      = defaultdict(lambda:SubjectivityTuple('','','',''))
        self._malformed = {}


        # File containing data
        filename = os.path.join(BASE_DIR, 'lexicons/SubjectivityClues/subjectivity-clues.tff')


        # Populate table with unigrams
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for lno,line in enumerate(f.readlines()):
                    match = re.search('type=(\w+) len=1 word1=([\w-]+) pos1=(\w+) stemmed1=(\w) priorpolarity=(\w+)', line)
                    if match:
                        typ   = match.group(1)
                        word  = match.group(2)
                        pos   = match.group(3)
                        stem  = match.group(4)
                        prior = match.group(5)
                        self._data[word] = SubjectivityTuple(typ,pos,stem,prior)
                    else:
                        # Line is wrong format
                        self._malformed[lno+1] = line.strip()
        else:
            print >>sys.stderr, 'ERROR: Unable to read unigrams from lexicon: SubjectivityClues'



    def lookup(self,word):
        return self._data[word]
