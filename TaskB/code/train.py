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
from sklearn.svm import LinearSVC
from sklearn import svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import f1_score
from sklearn.preprocessing import normalize as norm_mat

from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
"""
import sys
sys.path.append(os.getenv('BISCUIT_DIR'))
from common_lib.common_features.utilities import normalize_data_matrix
from scipy.sparse import csr_matrix
"""

BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')


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

    parser.add_argument("-g",
        dest = "grid",
        help = "Perform Grid Search",
        action='store_true',
        default = False
    )

    # Parse the command line arguments
    args = parser.parse_args()
    grid = args.grid


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
    train(X, Y, model_path, grid)




def train(X, Y, model_path=None, grid=False, feat_obj=None):

    """
    train()

    Purpose: Train a classifier on annotated data

    @param X.            list of (tweet-ID, tweet-text) pairs
    @param Y.            list of labels for each pair in X
    @param model_path.   filename of where to pickle Model object
    @param grid_search.  boolean indicating whether to perform grid search

    @return              A (svc,vec) pair, where:
                           svc is the classifer
                           vec is the feature vectorizer
    """


    # Data -> features
    if feat_obj == None: 
        feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)

    labels = [ labels_map[y] for y in Y ]
    Y = np.array( labels )


    # Vectorize feature dictionary
    # NOTE: import to fit() during training
    vec = DictVectorizer()
    #XNotNormalized = vec.fit_transform(feats)
    X = vec.fit_transform(feats)
    #print 'first: ', type(XNotNormalized.todense().view(type=np.ndarray))
    #print 'first: ', type(XNotNormalized.toarray())
    #print XNotNormalized.size
    #X = normalize_data_matrix(XNotNormalized)
    #XNotNormalized = np.ones((100,200))
    #print 'second: ', type(XNotNormalized)
    #print 'start norm'
    #X = csr_matrix( normalize_data_matrix(XNotNormalized.toarray()) )
    #print 'done norm'
    norm_mat( X , axis=0 , copy=False)

    # Grid Search
    if grid:
        print 'Performing Grid Search'
        clf = do_grid_search(X, Y)
    else:
        #clf = LinearSVC(C=0.1)
        #clf = LogisticRegression(C=0.1)
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



def do_grid_search(X, Y):

    # Search space
    C_range = 10.0 ** np.arange(-2, 9)
    param_grid = dict(C=C_range)
    cv = StratifiedKFold(y=Y, n_folds=10)

    grid = GridSearchCV(svm.LinearSVC(),
                        param_grid=param_grid,
                        cv=cv,
                        score_func=f1_score)

    # Search
    grid.fit(X, Y)

    print "The best classifier is: ", grid.best_estimator_
    return grid.best_estimator_




if __name__ == '__main__':
    main()
