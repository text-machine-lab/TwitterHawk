#-------------------------------------------------------------------------------
# Name:        evaluate.py
#
# Purpose:     Evaluate predictions based on precision, recall, and specificity
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import os
import os.path
import sys
import argparse
import glob

import helper
import model
from note import Note


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        help = "Files containing predictions",
        dest = "txt",
        default = os.path.join(BASE_DIR, 'predictions/*')
    )

    parser.add_argument("-r",
        help = "The directory that contains reference gold standard concept files",
        dest = "ref",
        default = os.path.join(BASE_DIR, 'data')
    )

    parser.add_argument("-o",
        help = "Write the evaluation to a file rather than STDOUT",
        dest = "output",
        default = None
    )

    # Parse command line arguments
    args = parser.parse_args()


    # Is output destination specified
    if args.output:
        args.output = open(args.output, "w")
    else:
        args.output = sys.stdout


    txt_files = glob.glob(args.txt)
    txt_files_map = helper.map_files(txt_files)


    for ref_directory in glob.glob(args.ref):

        #print 'ref_directory'
        #print ref_directory
        #print ''

        ref_files = os.listdir(ref_directory)
        ref_files = map(lambda f: os.path.join(args.ref, ref_directory, f), ref_files)
        ref_files_map = helper.map_files(ref_files)


        files = []
        for k in txt_files_map:
            if k in ref_files_map:
                files.append((txt_files_map[k], ref_files_map[k]))

        #print files

        # Compute the confusion matrix
        labels = model.labels_map   # hash tabble: label -> index
        confusion = [[0] * len(labels) for e in labels]


        # txt <- predicted labels
        # ref <- actual labels
        for txt, ref in files:

            # A note that represents the model's predictions
            cnote = Note()
            cnote.read( txt )

            # A note that is the actual concept labels
            rnote = Note()
            rnote.read( ref )

            # Get corresponding concept labels (prediction vs. actual)
            for c, r in zip( cnote.conlist(), rnote.conlist() ):
                confusion[labels[r]][labels[c]] += 1



        # Display the confusion matrix
        print >>args.output, ""
        print >>args.output, ""
        print >>args.output, ""
        print >>args.output, "================"
        print >>args.output, "PREDICTION RESULTS"
        print >>args.output, "================"
        print >>args.output, ""
        print >>args.output, "Confusion Matrix"
        pad = max(len(l) for l in labels) + 6
        print >>args.output, "%10s %10s" % (' ' * pad, "\t".join(labels.keys()))
        for act, act_v in labels.items():
            print >>args.output, "%10s %10s" % (act.rjust(pad), "\t\t\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in labels.items()]))
        print >>args.output, ""



        # Compute the analysis stuff
        precision = []
        recall = []
        specificity = []
        f1 = []
        accuracy = []

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        print >>args.output, "Analysis"
        print >>args.output, " " * pad, "Precision   Recall     Specificity      F1      Accuracy"



        for lab, lab_v in labels.items():
            tp = confusion[lab_v][lab_v]
            fp = sum(confusion[v][lab_v] for k, v in labels.items() if v != lab_v)
            fn = sum(confusion[lab_v][v] for k, v in labels.items() if v != lab_v)
            tn = sum(confusion[v1][v2] for k1, v1 in labels.items()
              for k2, v2 in labels.items() if v1 != lab_v and v2 != lab_v)
            precision += [float(tp) / (tp + fp + 1e-100)]
            recall += [float(tp) / (tp + fn + 1e-100)]
            specificity += [float(tn) / (tn + fp + 1e-100)]
            f1 += [float(2 * tp) / (2 * tp + fp + fn + 1e-100)]
            accuracy += [float(tp+tn) / (tp + fp +fn + tn + 1e-100)]
            print >>args.output, "%s %-12.4f%-12.4f%-14.4f%-12.4f%-12.4f" \
                                 % (lab.rjust(pad), precision[-1], recall[-1], specificity[-1], f1[-1], accuracy[-1])

        print >>args.output, "--------\n"


        print >>args.output, 'Macro-averaged pos/neg F-score: ', (f1[0] + f1[2]) / 2

        '''
        precision = sum(precision) / len(precision)
        recall = sum(recall) / len(recall)
        specificity = sum(specificity) / len(specificity)
        f1 = sum(f1) / len(f1)
        accuracy = sum(accuracy) / len(accuracy)

        print >>args.output, "Average: %.4f\t%.4f\t%.4f\t%.4f\t%.4f" % (precision, recall, specificity, f1, accuracy)
        '''


if __name__ == '__main__':
    main()
