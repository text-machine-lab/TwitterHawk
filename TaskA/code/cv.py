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

import train
import predict
import evaluate


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskA')



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

    parser.add_argument("-g",
        dest = "grid",
        help = "Perform Grid Search",
        type = bool,
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
    data = []
    for n in notes:
        d = [ it for it in zip(n.txtlist(), n.conlist()) ]
        data += d


    # Hacky way to average all predictions together
    # FIXME 
    #     Currently: collects every predicted label and evaluates all at once
    #     Should:    1. compute confusion matrix for each round of predictions
    #                2. Average confusion matrix (by storing running sum matrix)
    #                3. Display averaged matrix
    gold = []
    pred = []

    # For each held-out test set
    i = 1
    for training,testing in cv_partitions(data[:length], num_folds=num_folds):

        # Users like to see progress
        print 'Fold: %d of %d' % (i,num_folds)
        i += 1

        # Train on non-heldout data
        X_train = [ d[0] for d in training ]
        Y_train = [ d[1] for d in training ]
        vec,clf= train.train(X_train, Y_train, model_path=None, grid=False)

        # Predict on held out
        X_test = [ d[0] for d in testing ]
        Y_test = [ d[1] for d in testing ]
        labels = predict.predict(X_test, clf, vec)

        # Evaluate everything at once (hacky)
        gold += Y_test
        pred += labels


        # Evaluate
        #evaluate.evaluate(labels, Y_test)

    # Evaluate
    evaluate.evaluate(gold, pred)



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




if __name__ == '__main__':
    main()
