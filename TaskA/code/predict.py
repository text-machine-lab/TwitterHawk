#-------------------------------------------------------------------------------
# Name:        predict.py
#
# Purpose:     Predict on input files
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import glob
import argparse
import cPickle as pickle

from taska_features.features import FeaturesWrapper

from model import reverse_labels_map
from model import convert_labels
from note import Note


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskA')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "txt",
        help = "The files to be predicted on",
        default = os.path.join(BASE_DIR, 'data/test-gold-A.txt')
        #default = os.path.join(BASE_DIR, 'data/sms-test-gold-A.tsv')
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
    txt_files  = glob.glob(args.txt)
    model_path = args.model
    out_dir    = args.out


    # Available data
    if not txt_files:
        print 'no predicting files :('
        exit(1)


    # Load model
    with open(model_path+'.model', 'rb') as fid:
        clf = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)


    # Predict labels for each file
    feat_obj = FeaturesWrapper()
    for pfile in txt_files:
        note = Note()
        note.read(pfile)
        X = note.getTweets()

        # Predict
        labels = predict( X, clf, vec, feat_obj=feat_obj )

        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(pfile))
        note.write( outfile, labels )




def predict( X, clf, vec, feat_obj=None ):

    """
    predict()
    """

    # Data -> features
    if feat_obj == None: feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)

    # Vectorize feature dictionary
    # NOTE: do not fit() during predicting
    vectorized = vec.transform(feats)

    # predict
    labels = clf.predict(vectorized)
    labels = [ reverse_labels_map[y] for y in labels ]

    return labels



if __name__ == '__main__':
    main()
