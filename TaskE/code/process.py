#-------------------------------------------------------------------------------
# Name:        read_tweets.py
#
# Purpose:     Fetch tweets from file
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import argparse
import os
from collections import defaultdict

from emoticons import emoticon_type




def tweet_stream(tweets):

    with open(tweets,'r') as f:

        lines = f.readlines()

        for line in lines[:]:
            yield line.strip('\n')



def normalize(twt):
    return set(twt.split())



def main():


    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "tweets",
        help = "The file of tweets",
        default = os.path.join(os.path.dirname(__file__), '../data/tweets.txt')
    )

    args = parser.parse_args()


    tweets = args.tweets



    # Gather tweets
    data = tweet_stream(tweets)


    # Normalize tweets
    normalized = (  normalize(twt)  for  twt  in  data  )


    # Classify tweet sentiment
    senti = {'positive':[], 'negative':[]}
    for twt in normalized:

        # Ignore retweets
        if 'RT' in twt: continue

	pos = False
	neg = False

	for word in twt:

	    etype = emoticon_type(word)

	    if etype == 'positive':
		pos = True
	    if etype == 'negative':
		neg = True
		

	# If unique sentiment
	if pos and (not neg):
	    senti['positive'].append(twt)

	if neg and (not pos):
	    senti['negative'].append(twt)




    lex = defaultdict( lambda: {'positive':0, 'negative':0} )
    for e,twts in senti.items():
        for twt in twts:
            for word in twt:
                lex[word][e] += 1



    def senti_key(s):
        return s[1]['positive'] - s[1]['negative']


    limit = 4
    for k,v in sorted(lex.items(), key=senti_key, reverse=True):

        # Skip low frequencies
        if (v['positive'] < limit) and (v['negative'] < limit): continue

	print k, '\t\t', v




if __name__ == '__main__':
    main()
