######################################################################
#  CliCon - twitter_data.py                                          #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Gather features for tweet based on twitter metadata.     #
######################################################################


import sys, os
import argparse
from collections import defaultdict

import interface_twitter


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.cache           import Cache
from common_lib.common_features import utilities



class TwitterData:

    def __init__(self, sids=[], data=[]):
        # Tweet cache
        self.cache = Cache('twitter_data')

        # Cache all given data
        self.resolve(sids, data)



    def resolve(self, sids, data):

        """
        resolve()

        Purpose: Wrapper for interface_twitter.resolve() (to use object's cache)

        @param sids.  A list of twiiter IDs.
        @return       A list of tweets.
        """

        # Compile list of tweets that need to be quieried with API
        uncached = [  sid  for  sid  in  sids  if not self.cache.has_key(sid)  ]

        #print 'uncached: ', len(uncached)

        # Use API to lookup uncached tweets
        if uncached:
            partial = interface_twitter.resolve(uncached)
            for sid,twt in zip(uncached,partial):
                self.cache.add_map(sid,twt)

        # Get all tweets
        resolved = []
        for txt,sid in zip(data,sids):
            twt = self.cache.get_map(sid)
            if txt == twt['text']:
                res = twt
            else:
                res = None
            #print 'res: ', res
            resolved.append(res)

        return resolved



    def lookup(self, sids):

        """
        resolve()

        Purpose: Wrapper for interface_twitter.resolve() (to use object's cache)

        @param sids.  A list of twiiter IDs.
        @return       A list of tweets.
        """

        # Compile list of tweets that need to be quieried with API
        uncached = [  sid  for  sid  in  sids  if not self.cache.has_key(sid)  ]

        #print 'uncached: ', len(uncached)

        # Use API to lookup uncached tweets
        if uncached:
            partial = interface_twitter.resolve(uncached)
            for sid,twt in zip(uncached,partial):
                self.cache.add_map(sid,twt)

        # Get all tweets
        resolved = []
        for sid in sids:
            twt = self.cache.get_map(sid)
            resolved.append(twt)

        return resolved



    def features(self, sid):

        """
        features()

        Purpose: Get features from tweet meta data

        @param sids.  A tweet ID
        @return       A dictionary of meta data features.
        """

        # Get tweet
        tweet = self.cache.get_map(sid)

        if tweet == None: return {}

        # Extract features
        feats = {}

        # Not available
        if tweet['text'] == 'Not Available': return {}

        # Features: Retweet & Favorite counts
        feats['favorite_count' ] = tweet['favorite_count'] # 2
        feats['retweet_count'  ] = tweet['retweet_count']  # 1

        # Feature: Whether username contains word 'news'
        if 'news' in tweet['user']['screen_name'].lower():
            feats['is_news'] = 1
        if 'news' in tweet['user']['name'].lower():
            feats['is_news'] = 1

        # Feature: Whether tweet is reply
        if tweet['in_reply_to_status_id_str']:
            feats['is_reply'] = 1

        return feats




def main():

    # Parse arguments
    parser = argparse.ArgumentParser(description="downloads tweets")

    parser.add_argument('--partial', 
                        dest='partial', 
                        default=None, 
                        type=argparse.FileType('r')
                       )
    parser.add_argument('--dist', 
                        dest='dist', 
                        default=None, 
                        type=argparse.FileType('r'), 
                        required=True
                       )

    args = parser.parse_args()


    # Get an ID from the dist file
    sids   = []
    labels = []
    for line in args.dist:
        fields = line.strip().split('\t')
        sid   = fields[0]
        label = fields[2]
        sids.append(sid)
        labels.append(label)

    tdata = TwitterData(sids)




if __name__ == '__main__':
    main()
