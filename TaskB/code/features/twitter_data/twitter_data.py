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

sys.path.append(os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/code'))
from cache import Cache

sys.path.append(os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/code/features'))
import utilities



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
    #stats(sids,labels)

    #print features_list



class TwitterData:

    def __init__(self, sids=[]):
        # Tweet cache
        self.cache = Cache('twitter_data')

        # Cache all given data
        self.resolve(sids)


    def resolve(self, sids):

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
            #print uncached
            partial = interface_twitter.resolve(uncached)
            for sid,twt in zip(uncached,partial):
                self.cache.add_map(sid,twt)

        # Get all tweets
        return [  self.cache.get_map(sid)  for  sid  in  sids  ]



    def stats(self, sids, labels):

        """
        stats()

        Purpose: Statistics about features.
        """

        # Get all tweets
        tweets = self.resolve(sids)

        counts    = defaultdict(lambda:[])
        followers = defaultdict(lambda:[])
        favs      = defaultdict(lambda:[])
        totals    = defaultdict(lambda:[])
        for tweet,label in zip(tweets,labels):

            if tweet['text'] == 'Not Available': continue

            totals[label].append(tweet['text'])

            if tweet['favorite_count'] > 0:

                followers[label].append(tweet['user']['followers_count'])
                counts[label].append(   tweet['favorite_count']         )
                favs[label].append(     tweet['text']                   )

                continue

                print sid
                print label

                keys = ['text', 'favorite_count', 'retweet_count',
                        'created_at', 'in_reply_to_status_id', 'entities']
                for key in keys:
                    print key
                    if key in tweet:
                        print '\t', tweet[key]
                        print
                    else:
                        print '\t', None
                        print
                print '\n\n'


        for l in favs.keys():
            verbose = True
            twts  =    totals[l]
            found =      favs[l]
            c     =    counts[l]
            f     = followers[l]
            print
            print l, len(found), '/', len(twts)
            if verbose:
                for twt,count,follower in zip(found,c,f):
                    print twt , '\t(%d / %d)' % (count,follower)
                    print
            print '\n\n'



    def features(self, sid):

        """
        features()

        Purpose: Get features from tweet meta data

        @param sids.  A tweet ID
        @return       A dictionary of meta data features.
        """

        # Get all tweets
        tweet = self.cache.get_map(sid)


        # Extract features
        
        if tweet['text'] == 'Not Available': return {}


        # Feature dictionaries
        features = {}

        # Terrible features
        #features['followers_count'] = tweet['user']['followers_count']
        #features['statuses_count' ] = tweet['user']['statuses_count']


        # Good features
        #features['favorite_count' ] = tweet['favorite_count'] # 2
        features['retweet_count'  ] = tweet['retweet_count']   # 1

        # Not super hepful
        #if 'news' in tweet['user']['screen_name'].lower():
        #    features['is_news'] = 1
        #if 'news' in tweet['user']['name'].lower():
        #    features['is_news'] = 1

        # Group +.0005
        #if tweet['in_reply_to_status_id_str']:
        #    features['is_reply'] = 1


        '''
        for k,v in tweet.items():
            print k, v
            print
        print '\n\n\n'
        '''


        if tweet['in_reply_to_status_id']:
            reply = self.resolve( [tweet['in_reply_to_status_id']] )
            text = reply[0]['text'].split()
            normed = utilities.normalize_phrase(text, stem=True)
            for w in normed:
                features[('reply-unigram',w)] = .5


        return features




if __name__ == '__main__':
    main()
