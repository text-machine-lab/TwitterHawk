#-------------------------------------------------------------------------------
# Name:        train.py
#
# Purpose:     Train an svm
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sys
import os
import glob
import argparse
import cPickle as pickle
from collections import defaultdict


# Scikit-learn
import numpy as np
from sklearn.feature_extraction import DictVectorizer

from sklearn.svm import LinearSVC
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier

# My code
from note import Note, find_target
from tweet import Tweet, labels_map
from taskc_features.features import FeaturesWrapper



BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskC')




def main():

    """
    main()

    Purpose: This program builds an SVM model for Twitter classification
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        default = os.path.join(BASE_DIR, 'data/c-annotated.txt')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/C-awesome')
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Decode arguments
    txt_files = glob.glob(args.txt)
    model_path = args.model


    # Cannot train on empty list
    if not txt_files:
        print 'no training files :('
        exit(1)


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
        X += n.getTweets()
        Y += n.getLabels()


    # Train classifier
    train(X, Y, model_path)




def train(X, Y, model_path=None):

    # Extract features
    feat_obj = FeaturesWrapper()
    feats = extract_features(X, feat_obj)

    return train_vectorized(feats, Y, model_path)



def train_vectorized(X, Y, model_path=None):

    # Vectorize feature dictionary
    vec = DictVectorizer()
    X = vec.fit_transform(X)

    # Vectorize labels
    labels = [ labels_map[y] for y in Y ]
    Y = np.array(  labels  )

    clf = LinearSVC(C=0.1)
    #clf = svm.SVC(C=0.1, gamma=10.0)
    #clf = LogisticRegression(C=1000.0)
    #clf = SGDClassifier(penalty='elasticnet',alpha=0.001, l1_ratio=0.85, n_iter=1000,class_weight='auto')
    clf.fit(X, Y)

    # Save model
    #print 'train_vectorized: ', model_path
    if model_path:
        with open(model_path+'.dict' , 'wb') as f:
            pickle.dump(vec, f)

        with open(model_path+'.model', 'wb') as f:
            pickle.dump(clf, f)

    # return model
    return vec, clf




def extract_features(X, feat_obj=None):
    # Data -> features
    if feat_obj == None: feat_obj = FeaturesWrapper()
    return feat_obj.extract_features(X)






if __name__ == '__main__':
    main()
