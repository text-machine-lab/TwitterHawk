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

    #labels_list = frozenset( ['positive', 'negative', 'neutral', 'objective'] )
    labels_list = frozenset( ['positive', 'negative', 'neutral'] )


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
        self.uid   = words[1]
        self.begin = int(words[2])
        self.end   = int(words[3])
        self.label = words[4]

        # Robust against case where tweet actually contains tab character
        self.sent = []
        for segment in words[5:]:
            self.sent += segment.split(' ')


        # Remove "Not Available" tweets
        if ' '.join(self.sent) == 'Not Available':
            raise BadTweetException

        # Tweets must have legal indices
        length = len(self.sent)
        if (self.begin >= length) or (self.end >= length):
            #print 'ERROR: Bad index'
            #print '\t', self.begin, self.end, zip(range(length), self.sent)
            #print ''
            raise BadTweetException


        # Treat 'neutral' as 'objective'
        if self.label == 'objective':
            raise BadTweetException

        # ensure legal label
        #if self.label not in self.labels_list:
        #    self.label = 'neutral'



    def __str__(self):

        """
        Tweet::__str__()

        Purpose: Allow Tweet objects to be printable.
        """

        retVal = ''

        # Build output
        retVal +=                 self.sid
        retVal += '\t' +          self.uid
        retVal += '\t' +      str(self.begin)
        retVal += '\t' +      str(self.end  )
        retVal += '\t' +          self.label
        retVal += '\t' + ' '.join(self.sent)

        return retVal
