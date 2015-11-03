#-------------------------------------------------------------------------------
# Name:        train.py
#
# Purpose:     Train an svm
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import sys
import glob
import argparse
import cPickle as pickle


# TaskB code
from taskb_features.features import FeaturesWrapper
from model import labels_map
from note import Note


# Scikit-learn
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model       import SGDClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():

    """
    main()

    Purpose: This program builds an SVM model for Twitter classification
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        default = os.path.join(BASE_DIR, 'data/twitter-train-cleansed-B.tsv')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/awesome')
    )

    # Parse the command line arguments
    args = parser.parse_args()


    # Decode arguments
    txt_files = glob.glob(args.txt)
    model_path = args.model


    if not txt_files:
        print 'no training files :('
        sys.exit(1)


    # Read the data into a Note object
    notes = []
    for txt in txt_files:
        note_tmp = Note()
        note_tmp.read(txt)
        notes.append(note_tmp)

    # Get data from notes
    X = []
    Y = []
    for n in notes:
        X += zip(n.sid_list(), n.text_list())
        Y += n.label_list()

    # Build model
    train(X, Y, model_path)



def extract_features(X, feat_obj=None):
    # Data -> features
    if feat_obj == None:
        feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)
    return feats



def train(X, Y, model_path=None, feat_obj=None):

    """
    train()

    Purpose: Train a classifier on annotated data

    @param X.            list of (tweet-ID, tweet-text) pairs
    @param Y.            list of labels for each pair in X
    @param model_path.   filename of where to pickle Model object

    @return              A (svc,vec) pair, where:
                           svc is the classifer
                           vec is the feature vectorizer
    """


    # Data -> features
    feats  = extract_features(X, feat_obj=feat_obj)

    # Train
    return train_vectorized(feats, Y, model_path=model_path)



def train_vectorized(feats, Y, model_path=None):

    # Vectorize labels
    labels = [ labels_map[y] for y in Y ]
    Y = np.array( labels )

    # Vectorize feature dictionary
    vec = DictVectorizer()
    X = vec.fit_transform(feats)

    clf = SGDClassifier(penalty='elasticnet',alpha=0.001, l1_ratio=0.85, n_iter=1000,class_weight='auto')
    clf.fit(X, Y)

    # Save model
    if model_path:
        with open(model_path+'.dict' , 'wb') as f:
            pickle.dump(vec, f)

        with open(model_path+'.model', 'wb') as f:
            pickle.dump(clf, f)


    # return model
    return vec, clf




if __name__ == '__main__':
    main()
