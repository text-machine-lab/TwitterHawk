#-------------------------------------------------------------------------------
# Name:        profile.py
#
# Purpose:     Profile the code
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------



import os,sys
import re
import commands


def main():

    # Which script to profile
    if   'train'   in sys.argv:
        cmd = 'python -m cProfile   train.py'

    elif 'predict' in sys.argv:
        cmd = 'python -m cProfile predict.py'

    else:
        print '\n\tusage: profile.py <train|profile> <tottime|cumtime|percall>\n'
        exit(1)


    # Which field to sort by?
    fields = {'tottime':1, 'cumtime':3, 'percall':4}
    ind = 3
    for field,i in fields.items():
        if field in sys.argv:
            ind = i


    # Profile code
    status,output = commands.getstatusoutput(cmd)


    # Parse output
    regex= '\d+ function calls \(\d+ primitive calls\) in (\d+\.\d+) seconds([\S\s]*)'
    match = re.search(regex,output)
    time = match.group(1)
    output = match.group(2)

    # Sort data by cumulative call time for functions
    data = output.split('\n')[5:-2]
    data = sorted(data, key=lambda d: float(d.split()[ind]), reverse=True)

    # Display data
    print
    print 'time: %s seconds' % time
    print
    print '   ncalls  tottime  percall  cumtime  percall filename:lineno(function)'
    for line in data[:20]:
        print line



if __name__ == '__main__':
    main()
