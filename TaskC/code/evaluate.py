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
import glob

from note import Note
from tweet import labels_map
import helper


BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskC')



def main():

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        help = "Files containing predictions",
        dest = "txt",
        default = os.path.join(BASE_DIR, 'data/predictions/*')
    )

    parser.add_argument("-r",
        help = "The directory that contains reference gold standard concept files",
        dest = "ref",
        default = os.path.join(BASE_DIR, 'data')
    )

    parser.add_argument("-e",
        help = "Do error analysis",
        dest = "error",
        action = 'store_true'
    )


    # Decode arguments
    args = parser.parse_args()


    '''
    # Get pred data
    if not os.path.exists(pred_file):
        print 'no pred files :('
        sys.exit(1)
    pnote = Note()
    pnote.read(pred_file)
    pred_labels = pnote.getLabels()

    # Get gold data
    if not os.path.exists(gold_file):
        print 'no gold files :('
        sys.exit(1)
    gnote = Note()
    gnote.read(gold_file)
    gold_labels = gnote.getLabels()
    '''

    txt_files = glob.glob(args.txt)
    txt_files_map = helper.map_files(txt_files)


    ref_directory = args.ref


    ref_files = os.listdir(ref_directory)
    ref_files = map(lambda f: os.path.join(args.ref, ref_directory, f), ref_files)
    ref_files_map = helper.map_files(ref_files)


    files = []
    for k in txt_files_map:
        if k in ref_files_map:
            files.append((txt_files_map[k], ref_files_map[k]))


    print files


    # Useful for error analysis
    tweets = []

    # One list of all labels
    pred_labels = []
    gold_labels = []

    # txt <- predicted labels
    # ref <- actual labels
    for txt, ref in files:

        # A note that represents the model's predictions
        pnote = Note()
        pnote.read( txt )

        # A note that is the actual concept labels
        gnote = Note()
        gnote.read( ref )

        # Accumulate all predictions
        pred_labels += pnote.getLabels()
        gold_labels += gnote.getLabels()

        # Collect text for error analysis
        tweets += pnote.getTweets()


    print 'gold: ', len(gold_labels)
    print 'pred: ', len(pred_labels)

    # Evaluate predictions
    evaluate(pred_labels, gold_labels)


    # Error analysis
    if args.error:
        print '\n\n\n'
        error_analysis(tweets, pred_labels, gold_labels)






def evaluate(pred_labels, gold_labels, out=sys.stdout):

    """
    evaluate()

    Purpose: Useful for cross validation analysis
    """

    # Compute confusion matrix
    confusion = create_confusion(pred_labels, gold_labels)

    # Display confusion matrix
    display_confusion(confusion, out)



def create_confusion(pred_labels, gold_labels):

    # Compute the confusion matrix
    labels = labels_map
    confusion = [[0] * len(labels) for e in labels]

    # Get corresponding concept labels (prediction vs. actual)
    for p,g in zip( pred_labels, gold_labels ):
        confusion[labels[p]][labels[g]] += 1

    return confusion



def display_confusion(confusion, out=sys.stdout):

    # hash tabble: label -> index
    labels = labels_map

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
    print >>out, '     pred/gold '
    print >>out, "%10s %10s" % (' ' * pad, "\t\t".join(labels.keys()))
    for act, act_v in labels.items():
        print >>out, "%10s %10s" % (act.rjust(pad), "\t\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in labels.items()]))
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

    # FIXME - I think precision/recall were wrong (so I switched them)
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



def error_analysis(tweet_list, pred_labels, gold_labels):

    # False positives and false negatives
    pos_fp = []
    pos_fn = []
    neg_fp = []
    neg_fn = []

    for tweet,pred,gold in zip(tweet_list,pred_labels,gold_labels):

        start,end,text = tweet

        if pred != gold:
            print
            print 'pred: ', pred
            print 'gold: ', gold
            print
            print 'topic: ', ' '.join(text[start:end+1])
            print
            print ' '.join(text)
            print
            print '-'*80





if __name__ == '__main__':
    main()
