#-------------------------------------------------------------------------------
# Name:        cv.py
#
# Purpose:     Cross validation.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import argparse
import os
import glob
import random

from note import Note
from model import labels_map
from taskb_features.features import FeaturesWrapper

import train
import predict
import evaluate


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
        default = os.path.join(BASE_DIR, 'data/annotated.txt')
    )

    parser.add_argument("-n",
        dest = "length",
        help = "Number of data points to use",
        default = -1
    )

    parser.add_argument("-f",
        dest = "folds",
        help = "Number of folds to partition data into",
        default = 10
    )

    parser.add_argument("-r",
        dest = "random",
        help = "Random shuffling of input data.",
        action = 'store_true',
        default = False
    )


    # Parse the command line arguments
    args = parser.parse_args()


    # Decode arguments
    txt_files = glob.glob(args.txt)
    length = int(args.length)
    num_folds = int(args.folds)


    # Get data from files
    if not txt_files:
        print 'no training files :('
        sys.exit(1)

    notes = []
    for txt in txt_files:
        note_tmp = Note()
        note_tmp.read(txt)
        notes.append(note_tmp)

    # List of all data
    X = []
    Y = []
    for n in notes:
        # Data points
        x = [ it for it in zip(n.sid_list(), n.text_list()) ]
        X += x

        # Labels
        y = [ it for it in n.label_list() ]
        Y += y

    # Limit length
    X = X[:length]
    Y = Y[:length]

    # Build confusion matrix
    confusion = [ [0 for i in labels_map] for j in labels_map ]

    # Instantiate feat obj once (it'd really slow down CV to rebuild every time)
    feat_obj = FeaturesWrapper()

    # Extract features once
    feats = train.extract_features(X, feat_obj)
    data = zip(feats,Y)

    # For each held-out test set
    i = 1
    for training,testing in cv_partitions(data[:length], num_folds=num_folds, shuffle=args.random):

        # Users like to see progress
        print 'Fold: %d of %d' % (i,num_folds)
        i += 1

        # Train on non-heldout data
        X_train = [ d[0] for d in training ]
        Y_train = [ d[1] for d in training ]
        vec,clf = train.train_vectorized(X_train, Y_train, model_path=None, grid=False)

        # Predict on held out
        X_test = [ d[0] for d in testing ]
        Y_test = [ d[1] for d in testing ]
        labels = predict.predict_vectorized(X_test, clf, vec)

        # Compute confusion matrix for held_out data
        testing_confusion = evaluate.create_confusion(labels, Y_test)
        confusion = add_matrix(confusion, testing_confusion)


    # Evaluate
    evaluate.display_confusion(confusion)




def cv_partitions( data, num_folds=10, shuffle=True ):

    """
    cross_validation_partitions()

    Purpose: Parition input data for cross validation.

    @param data.    A list of data to partition
                     NOTE: does not look at what each element of the list is
    @param folds.   The number of folds to parition into

    @return         A list (actually generator) of tuples, where:
                       each tuple has (rest, heldout)
    """


    # Shuffle data
    if shuffle:
        random.shuffle(data)


    # Break data into num_folds number of folds
    fold_size = len(data) / num_folds
    folds = []
    for i in range(num_folds):
        f = [ data.pop() for j in range(fold_size) ]
        folds.append(f)


    # Evenly distribute any remaining data
    for i,d in enumerate(data):
        folds[i].append(d)


    # Which fold to hold out?
    for i in range(num_folds):
        heldout = folds[i]
        rest    = [ d   for lst     in folds[:i]+folds[i+1:] for d in lst]

        yield (rest, heldout)




def add_matrix(A, B):

    """
    add_matrix()

    Purpose: Element-wise sum of two matrices.
    """

    if len(A) != len(B): 
        raise Exception('Cannot add matrics of different dimensions')

    # Return value
    C = []

    for a,b in zip(A,B):

        if len(a) != len(b):
            raise Exception('Cannot add matrics of different dimensions')

        c = [ a_it+b_it for a_it,b_it in zip(a,b) ] 
        C.append(c)

    return C


if __name__ == '__main__':
    main()
