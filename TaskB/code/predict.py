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

import sys
back = os.path.dirname
base = back(back(back(os.path.abspath(__file__))))
sys.path.append( base )
from common_lib.common_features.utilities import normalize_data_matrix

from taskb_features.features import FeaturesWrapper
from model import reverse_labels_map
from note import Note


BASE_DIR = os.path.join(base,'TaskB')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "txt",
        help = "The files to be predicted on (e.g. data/demo.tsv)",
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model (e.g. models/demo.model)",
    )

    parser.add_argument("-o",
        dest = "out",
        help = "The directory to output predicted files (e.g. data/predictions)",
    )


    parser.add_argument("-p",
        dest = "prob",
        help = "State whether you want class probabilities, any non empty string",
    )


    # Parse the command line arguments
    args = parser.parse_args()

    if (not args.txt) or (not args.model) or (not args.out):
        parser.print_help()
        exit(1)

    # Decode arguments
    txt_files  = glob.glob(args.txt)
    model_path = args.model
    out_dir    = args.out
    if args.prob != '':
        prob = True
    else:
        prob = False

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
    for pfile in txt_files:
        note = Note()
        note.read(pfile)
        XNotNormalized = zip(note.sid_list(), note.text_list())
        X = XNotNormalized
        #X = normalize_data_matrix(XNotNormalized)

        # Predict
        labels = predict( X, clf, vec, prob=prob )

        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(pfile))
        note.write( outfile, labels )



def predict(X, clf, vec, feat_obj=None, prob=False):
    # Data -> features
    if feat_obj == None:
        feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)

    if prob:
        return predict_probs_vectorized(feats, clf, vec)
    else:
        return predict_vectorized(feats, clf, vec)



def predict_vectorized(feats, clf, vec):
    # Vectorize feature dictionary
    vectorized = vec.transform(feats)

    labels = clf.predict(vectorized)
    labels = [ reverse_labels_map[y] for y in labels ]

    return labels

def predict_probs_vectorized(feats, clf, vec):
    # Vectorize feature dictionary
    vectorized = vec.transform(feats)

    label_probs = clf.decision_function(vectorized)
    #labels = [ reverse_labels_map[y] for y in labels ]
    label_probs_list = []
    for i in range(label_probs.shape[0]):
        probs_list = list( label_probs[i][:] )
        str_list = [str(p) for p in probs_list]
        label_probs_list.append( '\t'.join(str_list) )

    return label_probs_list

class TwitterHawk(object):
    def __init__(self, model_path):
    # Load model
        with open(model_path+'.model', 'rb') as fid:
            self.clf = pickle.load(fid)
        with open(model_path+'.dict', 'rb') as fid:
            self.vec = pickle.load(fid)
        self.feat_obj = FeaturesWrapper()
    def predict(self, X, predict_type='label'):
    # Data -> features
        #feat_obj = FeaturesWrapper()
        feats  = self.feat_obj.extract_features(X)
        if predict_type == 'label':
            return self.predict_vectorized(feats)
        elif predict_type == 'probs':
            return self.predict_probs_vectorized(feats)

    def predict_probs_vectorized(self, feats):
        vectorized = self.vec.transform(feats)

        return self.clf.decision_function(vectorized)

    def predict_vectorized(self, feats):
        vectorized = self.vec.transform(feats)
        labels = self.clf.predict(vectorized)
        labels = [ reverse_labels_map[y] for y in labels ]
        return labels


if __name__ == '__main__':
    main()
