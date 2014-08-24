######################################################################
#  CliCon - interface_nlp.py                                         #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Provide a way for Python to utilize the output of the    #
#               twitter_nlp tagger.                                  #
#                                                                    #
#  Genia Tagger: https://github.com/aritter/twitter_nlp              #
######################################################################


import os,sys
import re
from commands import getstatusoutput



def resolve(tagger, data):

    '''
    resolve()

    Purpose: Call the twitter_nlp tagger and return its output in python format

    @param geniatagger.  A path to the executable extractEntities2.py
    @param data.         A list of tweet strings
    @return              A list of dictionaries of the tagger's output.
    '''


    # Write list to file in order to feed it to twitter_nlp
    tmp_out = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/etc/nlp_tmp_file.txt')
    with open(tmp_out, 'w') as f:
        for twt in data: 
            print >>f, twt


    # Build command to call tagger
    try:
        if not tagger: tagger = ''
        twitter_nlp = re.search('(.*\/twitter_nlp).*', tagger).group(1)
        cmd1 = 'export TWITTER_NLP=%s' % twitter_nlp
    except Exception:
        raise Exception('twitter_nlp not installed on system')

    cmd2 = 'python %s --pos --chunk --classify < %s' % (tagger,tmp_out)
    cmd = '%s ; %s' % (cmd1, cmd2)


    # Run twitter_nlp tagger
    print '\t\tRunning  twitter_nlp tagger'
    status,stream = getstatusoutput(cmd)
    tagged = stream.split('\n')[:-1]
    print '\t\tFinished twitter_nlp tagger'

    # Remove temp file
    os.remove(tmp_out)


    # Error from twitter_nlp?
    if status: raise Exception('Error with tagger. Invocation\n%s' % cmd)

    return [ twt.split() for twt in tagged ]

