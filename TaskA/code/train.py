#-------------------------------------------------------------------------------
# Name:        train.py
#
# Purpose:     Train an svm
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import glob
import argparse
import cPickle as pickle

from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import numpy as np
from sklearn import svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import f1_score
from sklearn.linear_model import SGDClassifier

from taska_features.features import FeaturesWrapper

from model import labels_map
from note import Note



BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskA')


def main():

    """
    main()

    Purpose: This program builds an SVM model for Twitter classification
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        #default = os.path.join(BASE_DIR, 'data/train-cleansed-A.txt')
        default = os.path.join(BASE_DIR, 'data/sample.txt')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/awesome')
    )

    parser.add_argument("-g",
        dest = "grid",
        help = "Perform Grid Search",
        action = 'store_true',
        default = False
    )

    # Parse the command line arguments
    args = parser.parse_args()
    grid = args.grid


    # Decode arguments
    txt_files = glob.glob(args.txt)
    model_path = args.model


    print model_path

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
        X += zip(n.getIDs(), n.getTweets())
        Y += n.getLabels()


    # Build model
    feat_obj = FeaturesWrapper()
    vec, svc = train(X, Y, model_path, grid, feat_obj)




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

    # Vectorize data
    X = extract_features(X, feat_obj)

    # Train model
    print 'train: ', model_path
    return train_vectorized(X, Y, model_path, grid)



def extract_features(X, feat_obj=None):
    # Data -> features
    if feat_obj == None: feat_obj = FeaturesWrapper()
    return feat_obj.extract_features(X)


def train_vectorized(X, Y, model_path=None, grid=False):

    # Vectorize labels
    labels = [ labels_map[y] for y in Y ]
    Y = np.array(  labels  )

    # Vectorize feature dictionary
    vec = DictVectorizer()
    X = vec.fit_transform(X)

    # Grid Search?
    if grid:
        print 'Performing Grid Search'
        clf = do_grid_search(X, Y)
    else:
        #clf = LogisticRegression(C=1000.0)
        clf = LinearSVC(C=0.1)
        #clf = svm.SVC(C=0.1, gamma=10.0)
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



def do_grid_search(X, Y):

    algorithm = 'linear_svm'
    #algorithm = 'maxent'
    #algorithm = 'rbf_svm'

    # Type of classifier
    if (algorithm == 'linear_svm'):
        print 'LINEAR_SVM'
        clf = svm.LinearSVC()

        # Search space
        C_range = 10.0 ** np.arange(-3, 2)   # best is 0.1
        param_grid = dict(C=C_range)

    elif (algorithm == 'maxent'):
        print 'MAXENT'
        clf = LogisticRegression()

        # Search space
        C_range = 10.0 ** np.arange(-3, 2)   # best is 1.0
        param_grid = dict(C=C_range)

    elif (algorithm == 'rbf_svm'):
        print 'RBF_SVM'
        clf = svm.SVC()

        # Search space
        C_range = 10.0 ** np.arange(-3, 2)              # best is  10.0
        gamma_range = 10.0 ** np.arange( -3 , 2 )       # best is  0.01
        param_grid = dict(C=C_range, gamma=gamma_range)


    # Cross validation folds
    cv = StratifiedKFold(y=Y, n_folds=10)

    # Grid Search
    grid = GridSearchCV(clf,
                        param_grid=param_grid,
                        cv=cv,
                        score_func=f1_score)

    # Search
    grid.fit(X, Y)

    print
    print "The best classifier is: ", grid.best_estimator_
    print
    print vars(grid.best_estimator_)
    return grid.best_estimator_




if __name__ == '__main__':
    main()
