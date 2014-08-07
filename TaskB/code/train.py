#-------------------------------------------------------------------------------
# Name:        train.py
# Purpose:     Train an svm
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import os
import sys
import glob
import argparse
import cPickle as pickle

from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
import numpy as np
from sklearn import svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import f1_score

import helper
from model import extract_features, extract_labels
from note import Note



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
        default = os.path.join(BASE_DIR, 'data/TaskB-Training.tsv')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The file to store the pickled model",
        default = os.path.join(BASE_DIR, 'models/awesome')
    )

    parser.add_argument("-g",
        dest = "grid",
        help = "Perform Grid Search",
        type = bool,
        default = False
    )

    # Parse the command line arguments
    args = parser.parse_args()
    grid = args.grid


    # Decode arguments
    txt_files = glob.glob(args.txt)
    model_path = args.model


    # Build model
    vec, svc = train(txt_files, model_path, grid)




def train(txt_files, model_path, grid=False):

    # ex. {'record-13': 'record-13.txt'}
    # ex. {'record-13': 'record-13.con'}
    txt_files_map = helper.map_files(txt_files)


    # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
    training_list = []
    for k in txt_files_map:
            training_list.append(txt_files_map[k])


    if not training_list:
        print 'no training files :('
        sys.exit(1)


    # Read the data into a Note object
    notes = []
    for txt in training_list:
        note_tmp = Note()
        note_tmp.read(txt)
        notes.append(note_tmp)


    # Data -> features
    feats  = extract_features(notes)
    labels = extract_labels(notes)
    Y = np.array(  labels  )


    # Vectorize feature dictionary
    # NOTE: import to fit() during training
    vec = DictVectorizer()
    X = vec.fit_transform(feats)


    # Grid Search
    if grid:
        print 'Performing Grid Search'
        clf = do_grid_search(X, Y)
    else:
        clf = LinearSVC(C=0.1)
        clf.fit(X, Y)


    # Save model
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
