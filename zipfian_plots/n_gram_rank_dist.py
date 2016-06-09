#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

# Demo code: http://matplotlib.org/examples/pylab_examples/legend_demo2.html

__version__ = "0.2.2"

import sqlite3
import collections
import logging
import os

import matplotlib.pyplot as plt
import numpy as np

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    dbs = [line.strip() for line in open(args.in_manifest, "r")]
    #colors = ["red", "green", "blue"]
    for (db_no, db) in enumerate(dbs):
        _logger.debug("Making line for database %r." % db)
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT term, tally FROM query;")
            d = dict()
            for row in cursor:
                d[row[0]] = row[1]
            c = collections.Counter(d)
            _logger.info("Most common 5: %r." % c.most_common(5))
            ranks = []
            tallies = []
            for (tuple_no, (term, tally)) in enumerate(c.most_common()):
                if tuple_no < 5:
                    _logger.info("Rank %r: %r." % (tuple_no+1, tally))
                ranks.append(tuple_no + 1)
                tallies.append(tally)
            top_1_percent = int(0.01 * len(ranks))
            _logger.info("1%% of N: %r of %r." % (top_1_percent, len(ranks)))
            #plt.scatter and plt.loglog are both called interchangeably
            #plt.loglog(np.array(ranks[top_1_percent:]), np.array(tallies[top_1_percent:]), c=colors[db_no], marker=".")
            plt.loglog(np.array(ranks), np.array(tallies), marker=".")
    #l, = plt.plot(np.array([1,2]), np.array([7,0]))
    #l, = plt.plot(np.array([3,4]), np.array([8,1]))
    #l, = plt.plot(np.array([5,6]), np.array([9,2]))

    # note that plot returns a list of lines.  The "l1, = plot" usage
    # extracts the first element of the list into l1 using tuple
    # unpacking.  So l1 is a Line2D instance, not a sequence of lines

    # Make a legend for specific lines.
    #plt.legend( (l2, l4), ('oscillatory', 'damped'), loc='upper right', shadow=True)
    plt.legend(("1-grams", "2-grams", "3-grams", "Whole path"))
    plt.grid(True)
    plt.xlabel('Frequency rank of token')
    plt.ylabel('Absolute frequency of token')
    plt.title(args.title)
    plt.savefig(args.out_file, format=args.out_format)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--out-format", default="pdf")
    parser.add_argument("--title", default="Term distribution of Registry path n-grams")
    parser.add_argument("in_manifest")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
