#-------------------------------------------------------------------------------
# Name:        length_filter.py
#
# Purpose:     Filter out tweet phrases that are not at least two 'k' long
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import argparse
import os

from note import Note



def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets', help='SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/out.txt'))
    args = parser.parse_args()

    # Arguments
    data = args.tweets


    # Note object
    note = Note()
    note.read( data )

    
    tweets = note.tweets
    text   = note.txtlist()

    # Count how many encountered labels
    limit  = 5
    out = []

    for txt,tweet in zip(text,tweets):

        # Must be at least 'limit' # of tweets
        if txt[1] - txt[0] + 1 >= limit:
            out.append(tweet)



    for twt in out:
        print twt



if __name__ == '__main__':
    main()
