#-------------------------------------------------------------------------------
# Name:        get_ids.py
#
# Purpose:     Collect the set of tweet IDs from a SemEval-formatted corpus
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import argparse
import os
import glob



def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets', help='SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/sample.txt'))
    args = parser.parse_args()

    # Arguments
    data = glob.glob(args.tweets)


    # Read data
    ids = set()
    for file in data:

        with open(file, 'r') as f:

            for line in f.readlines():

                # Tokenize
                toks = line.split()

                # Skip empty lines
                if not toks: continue

                # Get ID
                id = toks[0]
                ids.add(id)


    # Output list of IDs
    for id in ids:
        print id




if __name__ == '__main__':
    main()
