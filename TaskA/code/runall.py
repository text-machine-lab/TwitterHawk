#-------------------------------------------------------------------------------
# Name:        runall.py
#
# Purpose:     Train, predict, and evaluate the model.
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import train
import predict
import evaluate


def main():

    print 'TRAINING'
    train.main()

    print 'PREDICTING'
    predict.main()

    print 'EVAlUATING'
    evaluate.main()



if __name__ == '__main__':
    main()