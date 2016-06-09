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

__version__ = "0.3.0"

import logging
import os
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def main():
    conn = sqlite3.connect(args.in_db)
    conn.row_factory = sqlite3.Row

    df = pd.io.sql.read_sql("""\
SELECT
  *
FROM
  thresholds
WHERE
  dataset = '%s' AND
  NOT threshold IS NULL AND
  NOT %s IS NULL
;""" % (args.dataset, args.response_variable), conn)
    _logger.debug("Number of records in dataframe: %d." % len(df))

    #TODO File bug, marginal_kws["bins"] is null by default and not picking up a default value.
    g = sns.jointplot("threshold", args.response_variable, data=df, marginal_kws={"bins":50})

    plt.savefig(args.out_file, format="png")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("in_db")
    parser.add_argument("dataset")
    parser.add_argument("response_variable", choices=["precision", "recall", "f1"])
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
