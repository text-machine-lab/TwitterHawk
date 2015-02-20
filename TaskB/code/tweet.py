#-------------------------------------------------------------------------------
# Name:        tweet.py
#
# Purpose:     Internal representation of tweet
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



class BadTweetException(Exception):
    pass



class Tweet:

    #labels_list = frozenset( ['positive', 'negative', 'neutral'] )
    labels_list = frozenset( ['positive', 'negative', 'neutral', 'unknwn'] )


    # Constructor
    def __init__(self, line):

        """
        Tweet::Constructor

        Purpose: Parse a line of a SemEval file & store the representation.

        File format:         SID          UID        label        sentence
                 ex. 111344599699693568	338069340	neutral	   michael jackson - hollywood tonight http://t.co/s6n3HJj

        """

        words = line.split('\t')


        if words == ['\n']: raise BadTweetException


        self.sid   = words[0]
        self.uid   = words[1]
        self.label = words[2]
        self.sent  = words[3].strip('\n')


        # Remove "Not Available" tweets
        if self.sent == 'Not Available':
            raise BadTweetException

        # Adjust if possible
        if self.label == 'objective-OR-neutral': self.label = 'neutral'

        # ensure legal label
        if self.label not in self.labels_list:
            raise BadTweetException



    def __str__(self):

        """
        Tweet::__str__()

        Purpose: Allow Tweet objects to be printable.
        """

        retVal = ''

        # Build output
        retVal +=         self.sid
        retVal += '\t' +  self.uid
        retVal += '\t' +  self.label
        retVal += '\t' +  self.sent

        return retVal
