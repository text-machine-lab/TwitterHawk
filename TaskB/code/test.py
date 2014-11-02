#-------------------------------------------------------------------------------
# Name:        test.py
#
# Purpose:     Evaluate how well the system does on the SemEval 2014 data.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import argparse
import commands
import os

from collections import defaultdict
import cPickle as pickle

from predict import predict


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', dest='test_set', help='2014 test set.',
                        default='/data1/nlp-data/twitter/tools/scoring/B/annotated-B-filtered-2014.txt')

    parser.add_argument('-m', dest='model', help='trained ML model.',
                        default=os.path.join(os.getenv('BISCUIT_DIR'),'TaskB','models', 'awesome'))

    args = parser.parse_args()


    # Arguments
    data       = args.test_set
    model_path = args.model


    # Read SemEval 2014 data
    X = []
    with open(data, 'r') as f:
        for line in f.readlines():
            toks = line.split('\t')
            sid = toks[0]
            text = toks[3]
            X.append( (sid,text) )
    #X = zip(note.sid_list(), note.text_list())


    # Load model
    with open(model_path+'.model', 'rb') as fid:
        clf = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)


    #print X


    # Predict labels of data using model
    labels = predict( X, clf, vec )


    # Format output
    tmp_out = 'predictions.txt'
    with open(tmp_out,'w') as f:
        for i,label in enumerate(labels):
            print >>f, 'NA\t' + str(i+1) + '\t' + label


    # Call official scorer to evaluate results
    RUN_SCORER_CMD = 'perl /data1/nlp-data/twitter/tools/scoring/B/score-B-2014.pl %s' % tmp_out
    status,output = commands.getstatusoutput(RUN_SCORER_CMD)
    print output


    # Clean up
    os.remove(tmp_out)



if __name__ == '__main__':
    main()
