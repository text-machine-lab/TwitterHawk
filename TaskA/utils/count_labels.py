#-------------------------------------------------------------------------------
# Name:        count_labels.py
#
# Purpose:     Count the number of each labels from the SemEval data.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import argparse
import os

from collections import defaultdict


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets', help='SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/train-A.txt'))
    args = parser.parse_args()

    # Arguments
    data = args.tweets


    # Count how many encountered labels
    counts = defaultdict(lambda:0)
    with open(data,'r') as f:
        for line in f.readlines():
            label = line.split()[4]
            counts[label] += 1
    counts = dict(counts)

    # Display results
    print counts



if __name__ == '__main__':
    main()
