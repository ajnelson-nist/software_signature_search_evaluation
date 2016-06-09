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
Complete the ground truth table by augmenting ground truth positive to the whole of the cartesian product of node IDs and all training document names.

(This is probably the kind of thing that can be done with an EXISTS SQL query...)
"""

__version__ = "0.2.0"

import sqlite3
import os
import logging

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    inconn = sqlite3.connect(args.in_db)
    inconn.row_factory = sqlite3.Row
    incursor = inconn.cursor()

    outconn = sqlite3.connect(args.out_db)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    outcursor.execute("CREATE TABLE ground_truth(node_id STRING, doc_name STRING, present BOOLEAN);")

    node_ids = set()
    incursor.execute("SELECT DISTINCT node_id FROM ground_truth_positive;")
    for row in incursor:
        node_ids.add(row["node_id"])

    _logger.debug("Node IDs: %d." % len(node_ids))

    doc_names = set()
    with sqlite3.connect(args.training_db) as trainingconn:
        trainingconn.row_factory = sqlite3.Row
        trainingcursor = trainingconn.cursor()
        trainingcursor.execute("SELECT DISTINCT doc_name FROM ground_truth_positive;")
        for row in trainingcursor:
            doc_names.add(row["doc_name"])

    _logger.debug("Document names: %d." % len(doc_names))

    incursor.execute("SELECT DISTINCT * FROM ground_truth_positive;")
    for row in incursor:
        outcursor.execute("INSERT INTO ground_truth VALUES (?,?,1);", (row["node_id"], row["doc_name"]))

    all_pairs = []
    for node_id in node_ids:
        for doc_name in doc_names:
            all_pairs.append((node_id, doc_name))

    _logger.debug("Pairs: %d." % len(all_pairs))

    for pair in all_pairs:
        incursor.execute("SELECT COUNT(*) AS tally FROM ground_truth_positive WHERE node_id = ? AND doc_name = ?;", pair)
        row = incursor.fetchone()
        if row["tally"] == 0:
            outcursor.execute("INSERT INTO ground_truth VALUES (?,?,0);", pair)

    outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("training_db")
    parser.add_argument("in_db")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
