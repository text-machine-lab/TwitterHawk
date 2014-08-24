######################################################################
#  CliCon - nlp.py                                                   #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Interface for twitter_nlp tools.                         #
######################################################################


import os,sys
from collections import defaultdict
import string

import interface_nlp

# Add cache to path
sys.path.append( os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/code') )
from cache import Cache



class TwitterNLP:

    def __init__(self, tagger, data):
        # Lookup cache (constantly rerunning tagger takes time)
        cache = Cache('twitter_nlp')

        # Tag the data
        if tagger:

            # Tag all uncached data
            uncached = [  twt  for  twt  in  data  if  not  cache.has_key(twt)  ]
            if uncached:
                if tagger == 'cache':
                    msg = 'Uncached twitter_nlp data. Tagger must be installed.'
                    raise Exception(msg)
                partial = interface_nlp.resolve(tagger, uncached)
                for twt,tag in zip(uncached,partial):
                    cache.add_map(twt, tag)

            # Lookup all tags
            tagged = [  cache.get_map(twt)  for  twt  in  data  ]

        else:
            tagged = []

        # Store the data in an object
        self._words    = {}
        self._entities = {}
        self._pos      = {}
        self._events   = {}
        for twt,tags in zip(data,tagged):
            self._words[twt]    = [  '/'.join(t.split('/')[:-3]) for t in tags ]
            self._entities[twt] = [           t.split('/')[ -3]  for t in tags ]
            self._pos[twt]      = [           t.split('/')[ -2]  for t in tags ]
            self._events[twt]   = [           t.split('/')[ -1]  for t in tags ]
            #print self._words[twt]
            #print self._entities[twt]
            #print self._pos[twt]
            #print self._events[twt]
            #print



    def entities(self, twt):
        etype = None
        ents = []
        curr = []

        #print twt
        if twt not in self._words: return []

        for i in range(len(self._words[twt])):
            w   = self._words[   twt][i]
            tag = self._entities[twt][i]
            #print '\t', w, '\t', tag

            # Assumes 'I' never comes before a 'B'
            if tag[0] == 'I':
                curr.append(w)
            else:
                if curr:
                    ents.append( (etype,' '.join(curr)) )
                    curr = []

                if tag[0] == 'B':
                    etype = tag[2:]
                    curr = [w]

        # Flush remaining entity (if necessary)
        if curr: ents.append( (etype,' '.join(curr)) )

        #print ents
        return ents



    def features(self, twt):

        """
        features()

        Purpose: Get twitter_nlp features

        @param data. A list of tweet strings
        @return      A feature dictionary
        """

        # Feature dictionary
        features = {}


        '''
        # Feature: Entity types
        ents = self.entities(twt)
        for ent in ents:
            features[ ('entity_type', ent[0]) ] = 1
            #features[ ('entity', ent[1]) ] = 1
        '''


        '''
        # Feature: Entity types
        ents = self.entities(twt)
        for ent in ents:
            features[ ('entity_type', ent[0]) ] = 1
            features[ ('entity', ent[1]) ] = 1
        '''


        '''
        # Feature: POS counts
        pos_counts = defaultdict(lambda:0)        
        for pos in self._pos[twt]:
            if pos not in string.punctuation:
                pos_counts[pos] += 1
        for pos,count in pos_counts.items():
            featname = 'pos_count-%s' % pos
            features[featname] = count
        '''


        '''
        # Feature: POS counts
        pos_chunk_counts = defaultdict(lambda:0)        
        for pos in self._events[twt]:
            if pos != 'O':
                pos_chunk_counts[pos[2:]] += 1
        for pos,count in pos_chunk_counts.items():
            featname = 'pos_chunk_count-%s' % pos
            features[featname] = count
        '''


        '''
        print twt
        print features
        print
        '''


        return features

