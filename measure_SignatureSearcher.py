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

__version__ = "0.5.4"

import logging
import os
import pickle
import sqlite3
import collections

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    gtdict = dict()
    with sqlite3.connect(args.ground_truth_db) as gtconn:
        gtconn.row_factory = sqlite3.Row
        gtcursor = gtconn.cursor()
        gtcursor.execute("SELECT * FROM ground_truth;")
        for gtrow in gtcursor:
            gtdict[(gtrow["node_id"], gtrow["doc_name"])] = {
              0: False,
              1: True
            }.get(gtrow["present"])

    _logger.debug("Loading threshold dictionary...")
    doc_threshold = None
    with open(args.threshold_pickle, "rb") as fh:
        th_unpickler = pickle.Unpickler(fh)
        doc_threshold = th_unpickler.load()
    _logger.debug("Loaded threshold dictionary.")

    #List of tuples: node_id, doc_name, search score, is a hit (Boolean), is supposed to be a hit (Boolean ground truth)
    evaluation_tuples = []

    with open(args.query_results_manifest) as in_list_fh:
        for line in in_list_fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            filepath = cleaned_line
            filename = os.path.basename(filepath)
            if not filename.endswith(".pickle"):
                raise ValueError("Encountered a non-pickle file where only pickles were expected: %r." % filepath)
                continue

            node_id = filename.split(".pickle")[0]

            with open(filepath, "rb") as fh:
                unpickler = pickle.Unpickler(fh)
                results = unpickler.load()
                for (score, doc_name) in results:
                    #_logger.debug("Inspecting node_id %r, doc %r, score %r." % (node_id, doc_name, score))
                    #Report ground truth, with an absent record being null.
                    ground_truth_presence = gtdict.get((node_id, doc_name))

                    is_hit = None
                    threshold = doc_threshold.get(doc_name)
                    if not threshold is None:
                        is_hit = (score >= threshold)
                    evaluation_tuples.append((node_id, doc_name, score, threshold, is_hit, ground_truth_presence))

    with open(args.out_pickle, "wb") as fh:
        pickler = pickle.Pickler(fh)
        pickler.dump(evaluation_tuples)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("ground_truth_db")
    parser.add_argument("threshold_pickle")
    parser.add_argument("query_results_manifest")
    parser.add_argument("out_pickle")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
