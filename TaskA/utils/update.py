#-------------------------------------------------------------------------------
# Name:        update.py
#
# Purpose:     Update the Twitter cache for ID->text translation
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import argparse
import os


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets', help='SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/sample.txt'))
    args = parser.parse_args()

    # Arguments
    data = args.tweets


    # Load cache
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


    # Expand lookup cache
    with open(data, 'r') as f:

        for line in f.readlines():

            # Skip blank lines
            if not line: continue

            # Tokenize
            toks = line.split()

            # Skip blank lines
            if not toks: continue

            # Tweet ID
            id = toks[0]

            if len(toks) > 5:
                text = ' '.join(toks[5:])
                lookup[id] = text


    # Output new cache
    with open(cache, 'w') as f:
        for id,text in lookup.items():
            print >>f, id, text



if __name__ == '__main__':
    main()
