######################################################################
#  CliCon - nlp.py                                                   #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Interface for twitter_nlp tools.                         #
######################################################################


import argparse

import os,sys
from collections import defaultdict
import string

from HTMLParser import HTMLParser


import interface_nlp

# Add cache to path
sys.path.append( os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/code') )
from cache import Cache


def main():

    # Parse arguments
    parser = argparse.ArgumentParser(description='twitter_nlp tagging')

    parser.add_argument('-t',
                        dest = 'tweets',
                        default = None,
                        type=argparse.FileType('r')
                       )

    parser.add_argument('--tagger',
                        dest = 'tagger',
                        default = '/data1/wboag/biscuit/Biscuit/TaskB/etc/twitter_nlp/python/ner/extractEntities2.py'
                       )


    args = parser.parse_args()


    # Read data from file
    twts = [ line.split('\t')[3].strip('\n')  for  line  in  args.tweets.readlines() ]
    
    # twitter_nlp tagger
    tagger = args.tagger

    # Run twitter_nlp on data
    t_nlp = TwitterNLP(tagger, twts)

    # Display tokenized data
    toks = [ t_nlp.tokens(twt)  for  twt  in  twts ]



class TwitterNLP:

    def __init__(self, tagger, data):
        # Lookup cache (constantly rerunning tagger takes time)
        self.cache = Cache('twitter_nlp')

        # Output from the tagger
        self._words    = {}
        self._entities = {}
        self._pos      = {}
        self._events   = {}

        # Unescape data
        self.h = HTMLParser()

        # Resolve tweets
        self.tagger = tagger
        self.resolve(data)


    def resolve(self, data):

        #print 'resolve length: ', len(data)

        data = [ self.h.unescape(twt).strip() for twt in data ]

        # Tag the data
        if self.tagger:

            # Tag all uncached data
            uncached = [ twt for twt in data if not self.cache.has_key(twt) ]

            #print uncached
            #print 'len     : ', len(uncached)
            #print 'uncached: '
            #for twt in uncached: print '\t', twt
            #print '\n\n\n'

            if uncached:
                if self.tagger == 'cache':
                    msg = 'Uncached twitter_nlp data. Tagger must be installed.'
                    raise Exception(msg)
                partial = interface_nlp.resolve(self.tagger, uncached)
                for twt,tag in zip(uncached,partial):
                    self.cache.add_map(twt, tag)

            # Lookup all tags
            tagged = [ self.cache.get_map(twt) for twt in data ]

        else:
            tagged = []

        # Store the data in the object
        for twt,tags in zip(data,tagged):
            self._words[twt]    = [  '/'.join(t.split('/')[:-3]) for t in tags ]
            self._entities[twt] = [           t.split('/')[ -3]  for t in tags ]
            self._pos[twt]      = [           t.split('/')[ -2]  for t in tags ]
            self._events[twt]   = [           t.split('/')[ -1]  for t in tags ]
            #print twt
            #print self._words[twt]
            #print self._entities[twt]
            #print self._pos[twt]
            #print self._events[twt]
            #print



    def tokens(self, twt):
        twt = self.h.unescape(twt).strip()
        if twt not in self._words: 
            print 'not in: ', twt
            return []
        else:
            return self._words[twt]



    def entities(self, twt):
        twt = self.h.unescape(twt).strip()

        etype = None
        ents = []
        curr = []

        #print twt
        if twt not in self._words: return []

        for i in range(len(self._words[twt])):
            w   = self._words[   twt][i]
            tag = self._entities[twt][i]
            #print '\t', w, '\t', tag

            # Assumes 'I' never comes before a 'O'
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




    def brown(self, twt):
        twt = self.h.unescape(twt).strip()

        etype = None
        ents = []
        curr = []

        #print twt
        if twt not in self._words: return []

        for i in range(len(self._words[twt])):
            w   = self._words[   twt][i]
            tag = self._entities[twt][i]
            #print '\t', w, '\t', tag

            # Replace non-'O' with entity label
            if tag[0] != 'I':
                if curr:
                    ents.append( ' '.join(curr) )
                    curr = []

                if tag[0] == 'B':
                    curr = [tag[2:]]
                else:
                    curr = [w]


        # Flush remaining entity (if necessary)
        if curr: ents.append( ' '.join(curr) )

        #print ents
        #print 

        return ents



    def update(self, data):

        """
        update()

        Purpose: Run the tagger on a batch of tweets (rather than individually)

        @param data. A list of strings (each string is the text of a tweet)
        """

        self.resolve(data)



    def features(self, twt):

        """
        features()

        Purpose: Get twitter_nlp features

        @param twt.  The string text of a tweet.
        @return      A feature dictionary.
        """

        # Feature Evaluations:
        #
        # CV - 40 folds
        #
        # Baseline   - 0.632580027567
        # Entities   - 0.634127069003
        # Brown      - 0.629866566792
        # POS        - 0.634105466573
        # All        - 0.634953290389
        # Ents + POS - 0.633480942525


        # Feature dictionary
        features = {}


        # Escape text if not already done
        twt = self.h.unescape(twt).strip()


        # Feature: Entity types
        ents = self.entities(twt)
        for ent in ents:
            features[ ('entity_type', ent[0]) ] = .5
            features[ ('entity',      ent[1]) ] = .5


        # Feature: Brown Cluster bigrams
        clustered = self.brown(twt)
        for i in range(len(clustered)-1):
            bigram = clustered[i:i+2]
            features[ ('brown_bigram',(clustered[i],clustered[i+1])) ] = .5


        # Feature: POS counts
        pos_counts = defaultdict(lambda:0)        
        for pos in self._pos[twt]:
            if pos not in string.punctuation:
                pos_counts[pos] += 1
        for pos,count in pos_counts.items():
            featname = 'pos_count-%s' % pos
            features[featname] = count


        return features




# Reminder for self: Pizza in Olsen 311 - don't forget
if __name__ == '__main__':
    main()
