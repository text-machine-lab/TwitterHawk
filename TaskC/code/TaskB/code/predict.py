#-------------------------------------------------------------------------------
# Name:        predict.py
# Purpose:     Predict on input files
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import glob
import argparse
import cPickle as pickle

from sklearn.preprocessing import normalize as norm_mat

from taskb_features.features import FeaturesWrapper
from model import reverse_labels_map
from note import Note


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskC/code/TaskB')



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "txt",
        help = "The file to be predicted on",
        default = os.path.join(BASE_DIR, 'data/twitter-test-gold-B.tsv')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/awesome')
    )

    parser.add_argument("-o",
        dest = "out",
        help = "The directory to output predicted files",
        default = os.path.join(BASE_DIR, 'data/predictions')
    )


    # Parse the command line arguments
    args = parser.parse_args()


    # Decode arguments
    txt_file   = args.txt
    model_path = args.model
    out_dir    = args.out


    # Available data
    if not os.path.exists(txt_file):
        print 'no predicting files :('
        exit(1) 


    # Predict labels file
    note = Note()
    note.read(txt_file)

    XNotNormalized = zip(note.sid_list(), note.text_list())
    X = XNotNormalized

    # Predict
    labels = predict(X)

    # output predictions
    outfile  = os.path.join(out_dir, os.path.basename(txt_file))
    note.write( outfile, labels )




def predict_full_tweet_sentiment(X):

    """
    predict()
    """

    # Data -> features
    feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)

    # Load model
    model_path =os.path.join(os.path.dirname(__file__),'../models/B-all-vanilla')
    with open(model_path+'.model', 'rb') as fid:
        clf = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)

    # Vectorize feature dictionary
    vectorized = vec.transform(feats)
    norm_mat( vectorized , axis=0 , copy=False )

    # predict
    labels = clf.predict(vectorized)
    labels = [ reverse_labels_map[y] for y in labels ]

    return labels



if __name__ == '__main__':
    main()
