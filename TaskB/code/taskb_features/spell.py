

import enchant

import os
import sys
from string import punctuation
import re


# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)
from common_lib.read_config import enabled_modules
from common_lib.cache       import Cache

from common_lib.common_lexicons import emoticons



# for debugging
_debug = False
seen = set()



class SpellChecker:


    def __init__(self):

        # Global spell checker
        #self.d = enchant.DictWithPWL("en_US", '/data1/wboag/ml/twitvec/twitvec/spelling/output.txt')
        self.d = enchant.Dict("en_US")

        # Common abbreviations and mistakes
        self.common = {}
        abbrevs = os.path.join('/data1/nlp-data/twitter/tools/spell/abbrv.txt')
        with open(abbrevs,'r') as f:
            for line in f.readlines():
                if line == '\n': continue
                abbrev,full = tuple(line.strip('\n').split(' || '))
                self.common[abbrev] = full

        # Load cache of spell-corrected words
        self.cache = Cache('B-enchant')



    def correct_spelling(self, phrase, pos=None):

        #return phrase

        # Memoized?
        key = tuple(phrase)
        #if self.cache.has_key(key): 
        if False:
            return self.cache.get_map(key)

        cands = []

        # Build all possible candidates
        for i,w in enumerate(phrase):

            if _debug: print w

            # Special form
            if do_not_alter(w,pos,i):

                if _debug: print '\tSTATIC'
                cands.append([w])

            # Numbers
            elif re.search('\d',w):

                if _debug: print '\tNumber'
                cands.append(['000'])

            # Regexes
            elif re.search('^a*(?:h+q?a+)+h*$',w):
                if _debug: print '\tHAHA'
                cands.append(['haha'])
            elif re.search('^(?:h+e+)*$',w):
                if _debug: print '\tHEHE'
                cands.append(['haha'])
            elif re.search('^o*(?:xo)+x*$',w):
                if _debug: print '\tXOXO'
                cands.append(['xoxo'])
            elif re.search('^l(?:ol)+$',w):
                if _debug: print '\tLOLOL'
                cands.append(['lol'])

            # Common abbreviations / mistakes
            elif w.lower() in self.common:

                if _debug: print '\tCOMMON'
                cands.append([self.common[w.lower()]])

            # Normal
            else:

                # FIXME: do this during tokenization
                if w[-2:] ==  "'s": w = w[:-2]
                if w[-2:] ==  "'m": w = w[:-2]
                if w[-3:] == "'ve": w = w[:-2]
                if w[-3:] == "'ll": w = w[:-2]

                # ends in exlamation mark context
                exclamation = False
                if re.search('^[^!]*!$',w): 
                    w = w.strip('!')
                    exclamation = True

                # Capitalized often means proper noun
                if w[0].isupper():
                    if _debug: '\tMAYBE PROPER NOUN'
                    possible = [w]

                # Spelled correct?
                elif self.d.check(w):
                    if _debug: print '\tCORRECT!'
                    possible = [w]

                # Try fixing with repeated characters
                elif elongated_characters(w):
                    # Remove duplicated characters down to just 2 remaining
                    if _debug: print '\tELONGATED'
                    possible = [remove_duplicates(w)]
                    #print w, '\t->\t', possible[0]

                # Leading apostraphe
                elif (w[-1] == "'") and (self.d.check(w[:-1])):
                    if _debug: print '\tAPOSTRAPHE!'
                    possible = [w[:-1]]

                # Word not separated from punctuation
                elif (w[0] in punctuation) or (w[-1] in punctuation):
                    # Separate word from leading and trailing punctuation
                    match = re.search("([^a-zA-Z]*)([a-zA-z']*)([^a-zA-Z]*)",w)
                    leading,word,trailing = match.groups()

                    possible = []
                    if leading: possible.append(leading)
                    if word in self.common:
                        possible.append(self.common[word])
                    else:
                        possible.append(word)
                    if trailing: possible.append(trailing)

                    #print w, ' -> ', possible

                # Backoff to spell checker correction
                else:
                    if _debug: print '\tCHECKING SUGGESTIONS'

                    #if not self.cache.has_key(w):
                    if True: 

                        # Run spell ccorrection
                        possible = self.d.suggest(w)

                        # If no matches, then use original
                        if possible == []: 
                            possible = [w]

                        '''
                        if (w not in seen) and (edit_distance(w,possible[0])<=2):
                            seen.add(w)
                            print phrase[max(i-3,0):i+4]
                            print w, '\t', possible[0], '\t', edit_distance(w,possible[0])
                            print
                        '''

                        # good prediction?
                        if edit_distance(w,possible[0]) <= 2:
                            self.cache.add_map(key,possible)
                        else:
                            self.cache.add_map(key,w)

                    # lookup cached spell corrections
                    else:
                        possible = self.cache.get_map(w)

                # trailing exclamation 
                if exclamation:
                    possible = [ w + ' !' for w in possible ]

                cands.append(possible)

        #for c in cands:
        #    print c
        #print

        # Select proper candidate
        corrected = [ choices[0] for choices in cands ] 

        # memoize
        self.cache.add_map(key,corrected)

        return corrected




def do_not_alter(w,pos,i):

    # Empty word
    if w == '':                                 return True

    # All punctuation
    if all(c in punctuation for c in w):        return True

    # Hashtag
    if w[0] == '#':                             return True

    # Proper Noun
    if pos and pos[i]=='^':                     return True

    # Special symbol
    if w[0]=='<' and w[-1] == '>':              return True

    # User mention
    if w[0] == '@':                             return True

    # Common abbreviations
    if re.search('^(?:[a-zA-Z]\\.)+$',w):       return True

    # URL
    if w[:7] == 'http://':                      return True
    if re.search('www\\.',w):                   return True
    if re.search('\\.com',w):                   return True
    if re.search('t\\.co',w):                   return True

    # Emoticon
    if emoticons.emoticon_type(w):              return True

    # Not special
    return False




def elongated_characters(word):

    # Normalize
    word = word.lower()

    # If same letter repeated three times
    for i in range(len(word)-2):
        if not word[i].isalpha(): continue
        # This syntax for triple equality is allowed in Python
        if word[i] == word[i+1] == word[i+2]:
            return True

    # No matches
    return False



def remove_duplicates(w):

    # Normalize
    word = w.lower()
    retVal = []

    # If same letter repeated three times
    for i in range(len(word)-2):
        if not (word[i] == word[i+1] == word[i+2]):
            retVal.append(word[i])

    # Get last two characters
    retVal.append(word[-2:])

    # No matches
    return ''.join(retVal)



def edit_distance(s1, s2):
    m=len(s1)+1
    n=len(s2)+1

    tbl = {}
    for i in range(m): tbl[i,0]=i
    for j in range(n): tbl[0,j]=j
    for i in range(1, m):
        for j in range(1, n):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

    return tbl[i,j]



if __name__ == '__main__':
    text = 'Hallo my nume is bob'
    corrected = correct_spelling(text.split())
    print corrected
