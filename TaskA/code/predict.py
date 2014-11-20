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

    # Predict
    for txt_file in txt_files:
        note = Note()
        note.read(txt_file)
        X = zip(note.getIDs(),note.getTweets())

        labels = predict_using_model(txt_files, model_path, out_dir)

        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(txt_file))
        note.write( outfile, labels )



# Global variables (in case outside module repeatedly queries predict_using_model
clf = None
vec = None
feat_obj = None

def predict_using_model(X, model_path, out_dir):

    global clf,vec, feat_obj

    # Load model
    if clf == None:
        with open(model_path+'.model', 'rb') as fid:
            clf = pickle.load(fid)
    if vec == None:
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
