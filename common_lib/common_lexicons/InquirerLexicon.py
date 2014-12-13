from collections import defaultdict
from copy import copy
import os
import sys
#import re                                                                                                                                                    


# Add common-lib code to system path                                                                                                                          
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules

class InquirerLexicon( object ):

    def __init__(self):
        self._data = defaultdict(lambda:None)

        # File containing data          
        base_dir = enabled_modules['lexicons']
        filename = os.path.join(base_dir, 'GeneralInquirer/inquirerbasic.csv')
        #clusterSet = set([])
        for i,line in enumerate(open(filename).readlines()):

            if i == 0:
                self.blankTagDict = {t.lower():0 for t in line.strip('\n').split(',')[2:184]}
            else:
                lineSplit = line.strip('\n').split(',')[:184]
                word = lineSplit[0].lower()
                tags = [t.lower() for t in lineSplit[2:] if t != '']
                self._data[word] = tags

        """
            cluster, word = line.strip('\n').split('\t')[:2]
            self._data[word] = cluster
            clusterSet = clusterSet.union(set([cluster]))

        self.blankClusterDict = {c:0 for c in list(clusterSet)}
        """

    def getTags(self, token):
        return self._data[token]

    def getBlankDict(self):
        return copy(self.blankTagDict)
