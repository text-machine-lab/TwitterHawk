from collections import defaultdict
import os
import sys
#import re                                   


# Add common-lib code to system path        
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules

class ClusterLexicon( object ):

    def __init__(self):
        self._data = defaultdict(lambda:None)
        #self.allClusters = []

        # File containing data                                                              
        base_dir = enabled_modules['lexicons']
        filename = os.path.join(base_dir, 'BrownClusters/50mpaths2')
        clusterSet = set([])
        for line in open(filename).readlines():

            cluster, word = line.strip('\n').split('\t')[:2]
            self._data[word] = cluster
            clusterSet = clusterSet.union(set([cluster]))
        
        self.blankClusterDict = {c:0 for c in list(clusterSet)}

    def getCluster(self, token):
        return self._data[token]
         
    def getBlankDict(self):
        return self.blankClusterDict

