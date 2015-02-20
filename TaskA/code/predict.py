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

        labels,confidences = predict_using_model(X, model_path, out_dir)

        '''
        # Confident predictions
        labels_map = {'positive':0, 'negative':1, 'neutral':2}
        proxy = []
        for t,l,c in zip(note.getTweets(),labels,confidences):
            conf = []
            for i in range(len(labels_map)):
                if i == labels_map[l]: continue
                conf.append( c[labels_map[l]] - c[i] )
            avg = sum(conf) / len(conf)
            start,end,tweet = t
            if avg > 1:
                #print tweet[start:end+1]
                #print l
                #print c
                #print
                #proxy.append(l)
                proxy.append('poop')
            else:
                print 'not conf'
                print tweet[start:end+1]
                print l
                print c
                print
                proxy.append(l)
                #proxy.append('poop')
        '''


        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(txt_file))
        note.write( outfile, labels )
        #note.write( outfile, proxy )


def predict_using_model(X, model_path, out_dir):

    with open(model_path+'.model', 'rb') as fid:
        clf = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)
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
    confidences = clf.decision_function(vectorized)

    return labels,confidences



if __name__ == '__main__':
    main()
