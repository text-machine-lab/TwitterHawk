#-------------------------------------------------------------------------------
# Name:        count_labels.py
# Purpose:     Count the number of each labels from the SemEval data.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import argparse
import os



def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tweets', help='SemEval-formatted tweets',
                        default=os.path.join(os.path.dirname(__file__), '../data/TaskB-Training.tsv'))
    args = parser.parse_args()

    # Arguments
    data = args.tweets


    # Count how many encountered labels
    counts = {'objective': 0, 'positive': 0, 'negative': 0, 'neutral': 0, 'objective-OR-neutral':0}
    with open(data,'r') as f:
        for line in f.readlines():
            label = line.split()[2][1:-1]
            counts[label] += 1

    # Display results
    print counts



if __name__ == '__main__':
    main()
