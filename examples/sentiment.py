import sys
sys.path.append('/home/ppotash/_From Bell, Eric/ark-twokenize-py/')
sys.path.append('/home/ppotash/semeval15/Biscuit/TaskB/code')
from predict import TwitterHawk
from twokenize import tokenizeRawTweetText
from os import listdir
import json
from collections import defaultdict, Counter
import langid

def compute_polarity( in_counter ):
    total = 0
    polarity_count = 0
    for k in in_counter.keys():
        total += in_counter[k]
        if k == 'positive':
            polarity_count += in_counter[k]
        elif k == 'negative':
            polarity_count -= in_counter[k]
    return polarity_count / total


th = TwitterHawk('/home/ppotash/semeval15/Biscuit/TaskB/models/trained.model')

files = listdir('../data/us-to-russia/')

russia_tally = 0
putin_tally = 0
russia_list = []
putin_list = []
done_dict = defaultdict(bool)
for batch in files:
    with open('../data/us-to-russia/'+batch) as f:
        tweets = json.load(f)
        for t in tweets:
            if done_dict[t[u'id']] or langid.classify(t[u'text']) != 'en' or len(t[u'text']) == 0:
                continue
            else:
                text = t[u'text']
                tokens = tokenizeRawTweetText(text)
                if 'russia' in tokens:
                    print 'found russia'
                    russia_list.append(('0',text))# += tokens
                    russia_tally += 1
                if 'putin' in tokens:
                    print 'found putin'
                    putin_list.append(('0',text))# += tokens
                    putin_tally += 1
            done_dict[t[u'id']] = True

russia_labeled = th.predict(russia_list)
putin_labeled = th.predict(putin_list)
print compute_polairty(Counter(russia_labeled))
print compute_polarity(Counter(putin_labeled))

print Counter(russia_labeled)
print Counter(putin_labeled)
