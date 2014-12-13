

import enchant
import os
import string
import re



# Global spell checker
d = enchant.Dict("en_US")



# Common abbreviations and mistakes
common = {}
with open(os.path.join(os.getenv('BISCUIT_DIR'),'TaskB/etc/abbrv.txt'),'r') as f:
    for line in f.readlines():
        if line == '\n': continue
        abbrev,full = tuple(line.split())
        common[abbrev] = full



def do_not_alter(w,pos,i):

    # Empty word
    if w == '':                                 return True

    # All punctuation
    if all(c in string.punctuation for c in w): return True

    # Hashtag
    if w[0] == '#':                             return True

    # Proper Noun
    if pos and pos[i]=='^':                     return True

    # Special symbol
    if w[0]=='<' and w[-1] == '>':              return True

    # User mention
    if w[0] == '@':                             return True

    # URL
    if w[:7] == 'http://':                      return True

    # Not special
    return False



# for debugging
seen = []


def correct_spelling(phrase, pos=None):

    #return phrase

    cands = []

    # Build all possible candidates
    for i,w in enumerate(phrase):

        # Special form
        if do_not_alter(w,pos,i):

            cands.append([w])

        # Time
        elif re.search('\d+',w):

            cands.append(['<time>'])

        # Regexes
        elif re.search('a*(?:ha)+h*',w):
            cands.append(['laughing'])
        elif re.search('o*(?:xo)+x*',w):
            cands.append(['kisses'])

        # Common abbreviations / mistakes
        elif w in common:

            cands.append([common[w]])

        # Common abbreviations / mistakes
        elif w[-4:]=='neg' and w[:-4] in common:

            cands.append([common[w[:-4]]]+'_neg')

        # Normal
        else:

            # Negated?
            if w[-4:] == '_neg':
                w = w[:-4]
                neg = True
            else:
                neg = False

            # FIXME: do this during tokenization
            if w[-2:] == "'s": w = w[:-2]

            # Spelled correct?
            if d.check(w) or d.check(w[0].upper()+w[1:]):
                possible = [w]

            # Try fixing with repeated characters
            elif elongated_characters(w):
                # Remove duplicated characters down to just 2 remaining
                possible = [remove_duplicates(w)]
                #print w, '\t->\t', possible[0]

            # Backoff to spell checker correction
            else:
                possible = d.suggest(w)

                # If no matches, then use original
                if possible == []: 
                    possible = [w]

                '''
                if w not in seen:
                    seen.append(w)
                    print phrase[i-3:i+4]
                    print w, '\t', possible[0]
                    print
                '''

            possible = [ w.lower() for w in possible ]
            if neg: possible = [ w+'_neg' for w in possible ]
            cands.append(possible)

    #for c in cands:
    #    print c

    # Select proper candidate
    corrected = [ choices[0] for choices in cands ] 

    return corrected



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






if __name__ == '__main__':
    text = 'Hallo my nume is bob'
    corrected = correct_spelling(text.split())
    print corrected
