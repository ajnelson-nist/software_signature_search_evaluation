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
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    rcursor = conn.cursor()
    wcursor = conn.cursor()

    rcursor.execute("ATTACH DATABASE '%s' AS ss;" % args.in_db)

    work_tuples = []
    for dataset in ["evaluation", "m57"]:
        for response_variable in ["precision", "recall", "f1"]:
            work_tuples.append((dataset, response_variable))

    for work_tuple in work_tuples:
        (dataset, response_variable) = work_tuple
        metadict = dict()
        metadict["dataset"] = dataset
        metadict["response_variable"] = response_variable

        rcursor.execute("SELECT COUNT(*) AS tally FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%(dataset)s';" % metadict)
        row = rcursor.fetchone()
        total_tally = float(row["tally"])

        _logger.debug(total_tally)

        #Make bins
        rcursor.execute("SELECT %(response_variable)s, COUNT(*) AS tally FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%(dataset)s' GROUP BY %(response_variable)s ORDER BY %(response_variable)s;" % metadict)
        percentiles = dict() #Key: response variable (float); value: percentile (float)
        cumsum = 0.0
        for row in rcursor:
            percentiles[row[response_variable]] = cumsum
            cumsum += row["tally"] / total_tally

        wcursor.execute("""\
CREATE TABLE searcher_%(dataset)s_%(response_variable)s_percentiles (
  searcher_id TEXT,
  percentile NUMBER
);""" % metadict)

        rcursor.execute("SELECT searcher_id, %(response_variable)s FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%(dataset)s';" % metadict)
        for row in rcursor:
            percentile = percentiles[row[response_variable]]
            wcursor.execute("INSERT INTO searcher_%(dataset)s_%(response_variable)s_percentiles(searcher_id, percentile) VALUES (?,?);" % metadict, (row["searcher_id"], percentile))

        conn.commit()

    if args.debug:
        rcursor.execute("SELECT * FROM searcher_m57_precision_percentiles ORDER BY searcher_id LIMIT 10;")
        for row in rcursor:
            _logger.debug("Searcher %s:\t%r." % (row["searcher_id"], row["percentile"]))

        rcursor.execute("SELECT * FROM searcher_m57_recall_percentiles ORDER BY searcher_id LIMIT 10;")
        for row in rcursor:
            _logger.debug("Searcher %s:\t%r." % (row["searcher_id"], row["percentile"]))

        rcursor.execute("SELECT * FROM searcher_evaluation_recall_percentiles ORDER BY searcher_id LIMIT 10;")
        for row in rcursor:
            _logger.debug("Searcer %s:\t%r." % (row["searcher_id"], row["percentile"]))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("in_db")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
