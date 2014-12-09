#-------------------------------------------------------------------------------
# Name:        predict.py
#
# Purpose:     Predict on input files
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import sys
import glob
import argparse
import cPickle as pickle
from collections import defaultdict

from note import Note
from tweet import labels_map
from taskc_features.features import FeaturesWrapper


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskC')


reverse_labels_map = { i:label for label,i in labels_map.items() }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files to be predicted on",
        default = os.path.join(BASE_DIR, 'data/topics.txt')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/C-awesome')
    )

    parser.add_argument("-o",
        dest = "out",
        help = "The directory to output predicted files",
        default = os.path.join(BASE_DIR, 'data/predictions')
    )


    # Parse the command line arguments
    args = parser.parse_args()


    # Decode arguments
    txt_files  = glob.glob(args.txt)
    model_path = args.model
    out_dir    = args.out


    # Available data
    if not txt_files:
        print 'no predicting files :('
        exit(1)


    # Predict labels for each file
    for txt_file in txt_files:
        note = Note()
        note.read(txt_file)

        # predict
        X = note.getTweets()
        labels = predict_using_model(X, model_path)

        # Predict labels
        outfile  = os.path.join(out_dir, os.path.basename(txt_file))
        note.write( outfile, labels )


def predict_using_model(X, model_path, feat_obj=None):

    # Load model
    with open(model_path+'.model', 'rb') as fid:
        clf = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)
    if feat_obj == None:
        feat_obj = FeaturesWrapper()

    # Predict
    labels = predict( X, clf, vec, feat_obj=feat_obj )
    return labels



def predict( X, clf, vec, feat_obj=None ):

    """
    predict()
    """

    # Data -> features
    if feat_obj == None: feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)

    # predict
    return predict_vectorized(feats, clf, vec)



def predict_vectorized(X, clf, vec):
    # Vectorize feature dictionary
    vectorized = vec.transform(X)

    # predict
    labels = clf.predict(vectorized)
    labels = [ reverse_labels_map[y] for y in labels ]

    return labels




if __name__ == '__main__':
    main()
