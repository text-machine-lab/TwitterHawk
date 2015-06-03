######################################################################
#  CliCon - read_config.py                                           #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Read a configuration file to determine what features     #
#               are available on the system                          #
######################################################################



import os


# Open config file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filename = os.path.join( base_dir, 'config.txt' )


enabled_modules = {}
module_list = [ 'twitter_nlp', 'twitter_data', 'lexicons', 'hashtag', 'url', 'caches', 'ark_tweet', 'ukb_wsd' ]

with open(filename, 'r') as f:

    for line in f.readlines():
        words = line.split()
        if words:
            if words[0] in module_list:
                if words[1] == 'None':
                    enabled_modules[words[0]] = None
                else:
                    enabled_modules[words[0]] = words[1]
