#-------------------------------------------------------------------------------
# Name:        tweet.py
#
# Purpose:     Internal representation of tweet
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



class BadTweetException(Exception):
    pass


labels_list = frozenset( ['positive', 'negative', 'neutral'] )
labels_map = { label:i for i,label in enumerate(labels_list) }


class Tweet:


    # Constructor
    def __init__(self, line):

        """
        Tweet::Constructor

        Purpose: Parse a line of a SemEval file and store the internal representation.

        File format:         SID             UID       start-ind    end-ind     label                sentence
                 ex. 209814454601396224    207002102     0            5       objective   Venus will pass in front of the Sun.

        """

        words = line.strip().split('\t')

        if not words: raise BadTweetException

        self.sid   = words[0]
        self.topic = words[1]
        self.label = words[2]

        # Robust against case where tweet actually contains tab character
        self.tweet = '\t'.join(words[3:])

        # Remove "Not Available" tweets
        if self.tweet == 'Not Available':
            raise BadTweetException

        # Remove "off topic" tweets
        if self.label == 'off topic':
            raise BadTweetException

        # Remove tweets with bad labels
        if self.label not in labels_list:
            raise BadTweetException



    def __str__(self):

        """
        Tweet::__str__()

        Purpose: Allow Tweet objects to be printable.
        """

        retVal = ''

        # Build output
        retVal +=        self.sid
        retVal += '\t' + self.topic
        retVal += '\t' + self.label
        retVal += '\t' + self.tweet

        return retVal
