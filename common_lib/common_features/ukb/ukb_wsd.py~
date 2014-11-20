from subprocess import PIPE, Popen

import sys
sys.path.append('/home/ppotash/semeval15/Biscuit/common_lib')
from cache import Cache

class ukbWSD( object ):

    def __init__(self):
        self.cache = Cache('ukb_twitter')

    def ukb_wsd( self, tokenList , posList ):
    
        infile = 'context.txt'
        execLoc = '/data1/nlp-data/twitter/tools/ukb-2.0/bin/ukb_wsd'
        kb = '/data1/nlp-data/twitter/tools/ukb-2.0/bin/wn30.bin'
        kbDict = '/data1/nlp-data/twitter/tools/ukb-2.0/bin/wnet30_dict.txt'
        with open(infile,'w') as f:
            f.write('ctx_01\n')
            for i,(t,p) in enumerate(zip(tokenList, posList)):
                if p in ['N','V','A','R']:
                    f.write(t+'#'+p.lower()+'#w'+str(i)+'#1 ')
        p = Popen([execLoc, '--ppr', '--allranks', '-K', kb, '-D', kbDict, infile], stdout=PIPE)
        results = p.communicate()[0]
        return [ [tuple(wsd.split('/')) for wsd in l.split(' ')[3:-2]] for l in results.split('\n')[1:-1] ]
    
    """
    def isCached( self,txt ):
        return txt in self.cache.keys()

    def getCached( self,txt ):
        return self.cache[txt]
    
    """
