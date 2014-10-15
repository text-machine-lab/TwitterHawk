import os,sys
import argparse
import time
import datetime
from twitter import oauth_dance, read_token_file, Twitter, OAuth, TwitterError



# global connection
t = None

def connect():
    global t

    # Twitter credentials
    CONSUMER_KEY='JEdRRoDsfwzCtupkir4ivQ'
    CONSUMER_SECRET='PAbSSmzQxbcnkYYH2vQpKVSq2yPARfKm0Yl6DrLc'

    MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
    if not os.path.exists(MY_TWITTER_CREDS):
        oauth_dance("Semeval sentiment analysis", CONSUMER_KEY, CONSUMER_SECRET, MY_TWITTER_CREDS)
    oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
    t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))




def resolve(sids):

    """
    resolve()

    Purpose: Use the twitter api to get tweets from IDs.

    @param sids.  A list of twiiter IDs.
    @return       A list of tweets.
    """

    # Ensure connection
    if not t: connect()

    # Lookup each id
    tweets   = []
    resolved = []
    for sid in sids:

        print 'API lookup: ', sid

        # Resolve ID lookups
        while sid not in resolved:
            try:
                # Get tweet
                tweet = t.statuses.show(_id=sid) 
                resolved.append(sid)

            # Throttle API quieries
            except TwitterError as e:
                if e.e.code == 429:
                    rate = t.application.rate_limit_status()
                    reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                    now = datetime.datetime.today()
                    future = datetime.datetime.fromtimestamp(reset)
                    seconds = (future-now).seconds+1
                    if seconds < 10000:
                        sys.stderr.write("Rate limit exceeded, sleeping for %s seconds until %s\n" % (seconds, future))
                        time.sleep(seconds)
                else:
                    tweet = {'text':'Not Available'}
                    resolved.append(sid)

            except Exception, e:
                print >>sys.stderr, 'ERROR: Exception thrown with sid = ', sid
                print >>sys.stderr, e
                print >>sys.stderr
                break
                
        tweets.append(tweet)

    return tweets







def main():

    # Parse arguments
    parser = argparse.ArgumentParser(description="downloads tweets")

    parser.add_argument('--partial', 
                        dest='partial', 
                        default=None, 
                        type=argparse.FileType('r')
                       )
    parser.add_argument('--dist', 
                        dest='dist', 
                        default=None, 
                        type=argparse.FileType('r'), 
                        required=True
                       )

    args = parser.parse_args()


    # Get an ID from the dist file
    sids   = []
    labels = []
    for line in args.dist:
        fields = line.strip().split('\t')
        sid   = fields[0]
        label = fields[2]
        sids.append(sid)
        labels.append(label)


    # Lookup each tweet
    tweets = resolve(sids)



if __name__ == '__main__':
    main()
