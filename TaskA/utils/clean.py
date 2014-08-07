#-------------------------------------------------------------------------------
# Name:        clean.py
# Purpose:     Clean up data from SemEval downloads.
#
# A cleaned file entails:
#                    1) Remove 'Not Available' tweets
#                    2) Remove 'objective'     tweets
#
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import argparse
import os


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets' , help='downloaded SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/sample.txt'))
    parser.add_argument('-o', dest='out'    , help='"cleaned" SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/out.txt'))
    args = parser.parse_args()

    # Arguments
    tweets  = args.tweets
    out     = args.out


    # Read data
    output = clean(tweets)


    # Output cleaned data
    with open(out, 'w') as f:
        for line in output:
            print >>f, line



def clean(tweets):

    output = []
    with open(tweets, 'r') as f:

        for line in f.readlines():

            # Remove 'Not Available' data
            if 'Not Available' in line:
                continue

            # Tokenize
            toks = line.split()

            # Skip empty lines
            if not toks: continue

            # Remove 'objective' tweets
            if toks[4] == 'objective':
                continue

            # Stitch cleaned data back together
            text = ' '.join(toks[5:])
            cleaned = '\t'.join(toks[:5]) + '\t' + text

            output.append(cleaned)


    return output




if __name__ == '__main__':
    main()
