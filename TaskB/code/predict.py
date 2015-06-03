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
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize as norm_mat

from taskb_features.features import FeaturesWrapper
from model import reverse_labels_map
from note import Note


BASE_DIR = os.path.join(base,'TaskB')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "txt",
        help = "The files to be predicted on",
        default = os.path.join(BASE_DIR, 'data/twitter-test-gold-B.tsv')
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
    for pfile in txt_files:
        note = Note()
        note.read(pfile)
        XNotNormalized = zip(note.sid_list(), note.text_list())
        X = XNotNormalized
        #X = normalize_data_matrix(XNotNormalized)

        # Predict
        labels = predict( X, clf, vec )

        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(pfile))
        note.write( outfile, labels )




def predict(X, clf, vec, feat_obj=None):

    """
    predict()
    """

    #'''
    # Data -> features
    if feat_obj == None:
        feat_obj = FeaturesWrapper()
    feats  = feat_obj.extract_features(X)
    #'''
    #feats = []

    return predict_vectorized(feats, clf, vec)



def predict_vectorized(feats, clf, vec):

    # Vectorize feature dictionary
    # NOTE: do not fit() during predicting
    #'''
    vectorized = vec.transform(feats)
    norm_mat( vectorized , axis=0 , copy=False )

    confidences = clf.decision_function(vectorized)
    labels = clf.predict(vectorized)
    labels = [ reverse_labels_map[y] for y in labels ]

    with open('stuff-a','wb') as f:
        pickle.dump(confidences,f)
    with open('stuff-b','wb') as f:
        pickle.dump(labels,f)
    #'''

    '''
    with open('stuff-a','rb') as f:
        confidences = pickle.load(f)
    with open('stuff-b','rb') as f:
        labels = pickle.load(f)
    '''

    # Adjust edge cases of negative/neutrals
    adjusted = []
    for l,c in zip(labels,confidences):
        if l == 'negative':
            # Bias predictions toward neutral unless very confident
            if False: #((c[1]-c[2]) < 1) and (c[2] > 0):
            #if ((c[1]-c[2]) < 1) and (c[2] > 0):
                adjusted.append('neutral')
            else:
                #print c, '\t', c[1] - c[2]
                adjusted.append(l)
        else:
            adjusted.append(l)

    labels = adjusted


    #print '\n\n'

    #print clf
    #print '\n\n'
    #for k,v in vars(clf).items():
    #    print k
    #    print '\t', v
    #    print
    #print

    #print '\n\n'

    #print clf.decision_function(vectorized)

    #print '\n\n'

    return labels



if __name__ == '__main__':
    main()
