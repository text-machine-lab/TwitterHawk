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

from features.features import FeaturesWrapper
from model import extract_labels
from model import convert_labels
from note import Note


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')


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


    # Predict
    predict( txt_files, model_path, out_dir )




def predict( predict_files, model_path, out_dir ):

    if not predict_files:
        print 'no predicting files :('
        exit(1)


    # Load model
    with open(model_path+'.model', 'rb') as fid:
        svc = pickle.load(fid)
    with open(model_path+'.dict', 'rb') as fid:
        vec = pickle.load(fid)


    # Read the data into a Note object
    notes = []
    for pred_file in predict_files:

        note = Note()
        note.read(pred_file)

        # Data -> features
        feat_obj = FeaturesWrapper()
        feats  = feat_obj.extract_features([note])
        labels = extract_labels([note])


        # Vectorize feature dictionary
        # NOTE: do not fit() during predicting
        vectorized = vec.transform(feats)


        # predict
        labels = svc.predict(vectorized)
        labels = convert_labels( note, labels )

        # output predictions
        outfile  = os.path.join(out_dir, os.path.basename(pred_file))
        note.write( outfile, labels )



if __name__ == '__main__':
    main()
