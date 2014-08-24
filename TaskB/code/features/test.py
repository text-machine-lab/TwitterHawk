import os,sys
BASE_DIR = os.path.join(os.getenv('BISCUIT_DIR'),'TaskB')
sys.path.append( os.path.join(BASE_DIR, 'etc/patricia-trie-8') )
import patricia


T = patricia.trie('root', key='value', king='kong')
T['four'] = None

S = 'keys and kewl stuff'

print 'T                           ', T
print 'S                           ', S
print

print '"" in T:                    ', '' in T
print '"kong" in T                 ', 'kong' in T
print 'T["king"]                   ', T['king']
#print T['kong']
print
print 'len(T)                      ', len(T)
print 'sorted(T)                   ', sorted(T)
print 'T.key(S)                    ', T.key(S)
print 'T.value(S, 9)               ', T.value(S, 9)
print
del T['']
print 'T.item(S, 9, default=None)  ', T.item(S, 9, default=None)
print 'list(T.items(S))            ', list(T.items(S))
print 'T.isPrefix("kong")          ', T.isPrefix('k')
print 'T.isPrefix("kong")          ', T.isPrefix('kong')



'''
from pytrie import SortedStringTrie as trie
t = trie(an=0, ant=1, all=2, allot=3, alloy=4, aloe=5, are=6, be=7)
t['algorithm']=1
t['antoflag']=1
print t
print t.keys(prefix='al')
print t.longest_prefix('antonym')
'''
