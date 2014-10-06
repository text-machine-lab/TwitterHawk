#-------------------------------------------------------------------------------
# Name:        evaluate.py
#
# Purpose:     Evaluate predictions based on precision, recall, and specificity
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import os
import sys
import argparse

import model


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskA')



def main():

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        help = "Files containing predictions",
        dest = "tweets",
        default = os.path.join(BASE_DIR, 'data/predictions/test-gold-A.txt')
    )

    args = parser.parse_args()
    twts = args.tweets


    # Filename
    fname = os.path.basename(twts)


    # Build command for official evaluation script
    cmd = 'python ' + os.path.join(BASE_DIR,'utils/scorer.py')  + ' '   \
                    + 'a'                                       + ' '   \
                    + os.path.join(BASE_DIR,'data', fname)      + ' '   \
                    + twts


    # Run command
    os.system(cmd)




def evaluate(pred_labels, gold_labels, out=sys.stdout):

    """
    evaluate()

    Purpose: Useful for cross validation analysis
    """

    # Compute the confusion matrix
    labels = model.labels_map   # hash tabble: label -> index
    confusion = [[0] * len(labels) for e in labels]

    # Get corresponding concept labels (prediction vs. actual)
    for p,g in zip( pred_labels, gold_labels ):
        confusion[labels[p]][labels[g]] += 1

    # Display the confusion matrix
    print >>out, ""
    print >>out, ""
    print >>out, ""
    print >>out, "================"
    print >>out, "PREDICTION RESULTS"
    print >>out, "================"
    print >>out, ""
    print >>out, "Confusion Matrix"
    pad = max(len(l) for l in labels) + 6
    print >>out, "%10s %10s" % (' ' * pad, "\t".join(labels.keys()))
    for act, act_v in labels.items():
        print >>out, "%10s %10s" % (act.rjust(pad), "\t\t\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in labels.items()]))
    print >>out, ""

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

    print >>out, "Analysis"
    print >>out, " " * pad, "Precision   Recall     Specificity      F1      Accuracy"

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
        print >>out, "%s %-12.4f%-12.4f%-14.4f%-12.4f%-12.4f" \
                             % (lab.rjust(pad), precision[-1], recall[-1], specificity[-1], f1[-1], accuracy[-1])

    print >>out, "--------\n"

    print >>out, 'Macro-averaged pos/neg F-score: ', (f1[0] + f1[2]) / 2





if __name__ == '__main__':
    main()
