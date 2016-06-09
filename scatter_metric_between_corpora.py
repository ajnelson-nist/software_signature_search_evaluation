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

__version__ = "0.2.0"

import sqlite3

import pandas as pd
import matplotlib.pyplot as plt

def main():
    conn = sqlite3.connect(args.searcher_scores_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    metadict = dict()
    metadict["metric"] = args.metric.lower()

    df = pd.io.sql.read_sql("""\
SELECT
  e.%(metric)s AS score_eval,
  m.%(metric)s AS score_m57
FROM
  (SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "evaluation") AS e,
  (SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "m57") AS m
WHERE
  e.searcher_id = m.searcher_id AND
  e.sequences <> "experiment1"
ORDER BY
  score_eval DESC,
  score_m57 DESC
;""" % metadict, conn)
    xs = df["score_eval"]
    ys = df["score_m57"]
    s = plt.scatter(xs, ys)

    s.axes.set_xlim(-0.05,1.05)
    s.axes.set_ylim(-0.05,1.05)

    plt.xlabel("%s against evaluation machine" % args.metric)
    plt.ylabel("%s against M57" % args.metric)
    plt.savefig(args.out_pdf)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("searcher_scores_db")
    parser.add_argument("metric", choices={"Precision", "Recall", "F1"})
    parser.add_argument("out_pdf")
    args = parser.parse_args()

    main()
