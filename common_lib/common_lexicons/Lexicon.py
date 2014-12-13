#-------------------------------------------------------------------------------
# Name:        Lexicon.py
#
# Purpose:     Base class for all lexicons
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


from collections import defaultdict
import os
import sys
import re





# Add common-lib code to system path
sources = os.getenv('BISCUIT_DIR')
if sources not in sys.path: sys.path.append(sources)

from common_lib.read_config import enabled_modules



# Base class
class Lexicon:

    def __init__(self):
        raise Exception("Lexicon is abstract class")

    def lookup(self,word):
        raise Exception("Lexicon is abstract class. Must overload lookup()")
