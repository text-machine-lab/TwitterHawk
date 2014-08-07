#-------------------------------------------------------------------------------
# Name:        lookup.py
#
# Purpose:     Resolve ID->text translation (without Twitter API)
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import argparse
import os

from clean import clean


def load_cache():

    lookup = {}
    cache = os.path.join(os.path.abspath(__file__),'../../data/id_cache.txt')
    with open(cache, 'r') as f:
        for line in f.readlines():

            # Tokenize
            toks = line.split()

            # Skip blank lines
            if not toks: continue

            # Parse
            id = toks[0]
            text = ' '.join(toks[1:])

            # Add to cache
            lookup[id] = text

    return lookup



def lookup_tweets(lookup, data):

    tweets = clean(data)

    for twt in tweets:

        tok = twt.split()
        id = tok[0]

        if id in lookup:
            print '\t'.join(tok) + '\t' + lookup[id]



def count_resolved(lookup, data):

    pass



def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets', help='SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__),
                                             '../data/train/cleansed/twitter-train-cleansed-A.tsv'))
    parser.add_argument('--resolve', dest='resolve', help='Translate ID->text from "tweets"',
                        action='store_true')
    parser.add_argument('--count', dest='count', help='Count number of cache misses from "tweets"',
                        action='store_true')
    args = parser.parse_args()

    # Arguments
    data    = args.tweets
    count   = args.count    #or True
    resolve = args.resolve  or True


    # Load cache
    lookup = load_cache()


    # Translate IDs
    if resolve:
        lookup_tweets(lookup, data)

    # Count cache misses
    if count:
        count_resolved(lookup,data)




if __name__ == '__main__':
    main()
