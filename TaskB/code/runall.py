

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