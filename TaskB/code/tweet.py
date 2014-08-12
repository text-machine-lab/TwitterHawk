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

    labels_list = frozenset( ['positive', 'negative', 'neutral'] )


    # Constructor
    def __init__(self, line):

        """
        Tweet::Constructor

        Purpose: Parse a line of a SemEval file and store the internal representation.

        File format:         SID             UID       start-ind    end-ind     label                sentence
                 ex. 209814454601396224    207002102     0            5       objective   Venus will pass in front of the Sun.

        """

        words = line.split('\t')


        if words == ['\n']: raise BadTweetException


        self.SID   = words[0]
        self.UID   = words[1]
        self.label = words[2].strip('"')
        self.sent  = words[3]


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
        retVal +=              self.SID
        retVal += '\t' +       self.UID
        retVal += '\t' + '"' + self.label + '"'
        retVal += '\t' +       self.sent

        return retVal
