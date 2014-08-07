#-------------------------------------------------------------------------------
# Name:        read-db.py
# Purpose:     Read database
#
# Author:      Willie Boag
#-------------------------------------------------------------------------------


import sqlite3 as lite
import os



def main():


    # Connect to database
    dbname = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../all.db')
    con = lite.connect(dbname)

    with con:

        cur = con.cursor()


        # Confirm success
        cur.execute('SELECT text from Tweets')
        data = cur.fetchall()


    print ''
    for twt in data[:]:
        for txt in twt:
            txt = txt.replace('\n','\t')
            print txt.encode('ascii', 'ignore')


if __name__ == '__main__':

    main()
