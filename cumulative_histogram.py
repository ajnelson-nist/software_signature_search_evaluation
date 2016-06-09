#!/usr/bin/env python3

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

"""
Thanks to the matplotlib/numpy CDF code, abused into a cumulative histogram:
<https://stackoverflow.com/a/11692365>

Note that because we are not measuring a statistical distribution, this is NOT a cumulative distribution function.  It is simply a cumulative histogram.
"""

__version__ = "0.1.0"

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def cumulative_histogram_to_output_pdf(conn, dataset, variable, x_axis_label, out_file):
    metadict = {
      "dataset": dataset,
      "response_variable": variable
    }
    df = pd.io.sql.read_sql("SELECT %(response_variable)s FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%(dataset)s' AND NOT %(response_variable)s IS NULL;" % metadict, conn)

    xs = df[variable]
    ys = np.arange(len(xs)) / float(len(xs))
    _logger.debug("len(xs) = %d." % len(xs))

    #Make "empirical CDF"
    sorted_xs = np.sort(xs)
    p = plt.plot(sorted_xs, ys)
    plt.axes().set_xlim(0,1)

    plt.xlabel(x_axis_label, fontsize=20)
    plt.ylabel("%", fontsize=20)

    plt.savefig(out_file)

def main():
    conn = sqlite3.connect(args.in_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cumulative_histogram_to_output_pdf(conn, args.dataset, args.variable, args.x_axis_label, args.out_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("in_db")
    parser.add_argument("dataset")
    parser.add_argument("variable")
    parser.add_argument("x_axis_label")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
