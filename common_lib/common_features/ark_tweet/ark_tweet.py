######################################################################
#  CliCon - ark_tweet.py                                             #
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


from ark_tweet_nlp_python import CMUTweetTagger



# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.cache import Cache
from common_lib.read_config import enabled_modules


class ArkTweetNLP:

    def __init__(self, data=[]):
        # Lookup cache (constantly rerunning tagger takes time)
        self.cache = Cache('ark_tweet')

        # Unescape data
        self.h = HTMLParser()

        # Resolve and cache all currently uncached tweets
        self.resolve(data)

        print 'ARK-TWEET-FEATURES-NOT-IMPLEMENTED'

    def resolve(self, data):

        #print 'resolve length: ', len(data)

        data = [self.h.unescape(twt).strip() for twt in set(data)]

        # Tag all uncached data
        uncached = [ twt for twt in data if not self.cache.has_key(twt) ]

        #print uncached
        #print 'len     : ', len(uncached)
        #print 'uncached: '
        #for twt in uncached: print '\t', twt
        #print '\n\n\n'

        if uncached:
            #print 'uncached: ', uncached
            partial = CMUTweetTagger.runtagger_parse(uncached)
            #print 'partial: ', partial
            for twt,tag in zip(uncached,partial):
                self.cache.add_map(twt, tag)

        # Lookup all tags
        tagged = [ self.cache.get_map(twt) for twt in data ]

        #print 'TAGGED DATA'
        #print tagged
        return

        # Store the data in the object
        for twt,tags in zip(data,tagged):
            self._words[twt]    = [  '/'.join(t.split('/')[:-3]) for t in tags ]
            self._entities[twt] = [           t.split('/')[ -3]  for t in tags ]
            self._pos[twt]      = [           t.split('/')[ -2]  for t in tags ]
            self._events[twt]   = [           t.split('/')[ -1]  for t in tags ]
            #print 'tweet:    ', twt
            #print 'words:    ', self._words[twt]
            #print 'entities: ', self._entities[twt]
            #print 'POS:      ', self._pos[twt]
            #print 'events:   ', self._events[twt]
            #print



    def update(self, data):

        """
        update()

        Purpose: Run the tagger on a batch of tweets (rather than individually)

        @param data. A list of strings (each string is the text of a tweet)
        """


        return [] 

        self.resolve(data)



    def features(self, twt):

        """
        features()

        Purpose: Get twitter_nlp features

        @param twt.  The string text of a tweet.
        @return      A feature dictionary.
        """


        return {}

        # Feature dictionary
        feats = {}

        # Escape text if not already done
        twt = self.h.unescape(twt).strip()

        # Feature: Entity types
        ents = self.entities(twt)
        for ent in ents:
            feats[ ('entity_type', ent[0]) ] = .5
            feats[ ('entity',      ent[1]) ] = .5

        # Feature: Brown Cluster bigrams
        clustered = self.brown(twt)
        for i in range(len(clustered)-1):
            bigram = clustered[i:i+2]
            feats[ ('brown_bigram',(clustered[i],clustered[i+1])) ] = .5

        # Feature: POS counts
        pos_counts = defaultdict(lambda:0)        
        for pos in self._pos[twt]:
            if pos not in string.punctuation:
                pos_counts[pos] += 1
        for pos,count in pos_counts.items():
            featname = 'pos_count-%s' % pos
            feats[featname] = count

        #print 'nlp: ', twt
        #print '\t', feats

        return feats




def main():

    # Parse arguments
    parser = argparse.ArgumentParser(description='twitter_nlp tagging')

    parser.add_argument('-t',
                        dest = 'tweets',
                        default = None,
                        type=argparse.FileType('r')
                       )

    args = parser.parse_args()


    # Read data from file
    twts = [ line.split('\t')[3].strip('\n')  for  line  in  args.tweets.readlines() ]
    
    # Run twitter_nlp on data
    t_nlp = TwitterNLP(twts)

    # Display tokenized data
    toks = [ t_nlp.tokens(twt)  for  twt  in  twts ]




# Reminder for self: Pizza in Olsen 311 - don't forget
if __name__ == '__main__':
    main()
