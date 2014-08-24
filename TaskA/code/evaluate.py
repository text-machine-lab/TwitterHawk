#-------------------------------------------------------------------------------
# Name:        evaluate.py
#
# Purpose:     Evaluate predictions based on precision, recall, and specificity
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import os
import argparse


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





if __name__ == '__main__':
    main()
