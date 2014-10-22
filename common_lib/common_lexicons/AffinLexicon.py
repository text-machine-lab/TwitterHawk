from collections import defaultdict
import os
import sys
#import re


# Add common-lib code to system path                                                            
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules

class AffinLexicon( object ):
    
    def __init__(self):
        self._data = defaultdict(lambda:None)

        # File containing data           
        base_dir = enabled_modules['lexicons']
        filename = os.path.join(base_dir, 'Affin/AFINN-111.txt')

        for line in open(filename).readlines():
            word, score = line.strip('\n').split('\t')
            self._data[word] = int(score)

    def score(self, word):
        return self._data[key]
        """
        for key in self._data.keys():
            if key == word:
                return self._data[key]
            elif key[0] > word[0]:
                return None
        """
