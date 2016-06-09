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

__version__ = "0.2.2"

import logging
import os
import pickle
import sqlite3
import collections

_logger = logging.getLogger(os.path.basename(__file__))

import TFIDFEngine
import SignatureSearcher

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

    engine = TFIDFEngine.BasicTFIDFEngine()
    engine.load(args.vsm_pickle)

    searcher = SignatureSearcher.SignatureSearcher(engine)

    #Key: doc_name.
    #Value: List of scores for *all* ground truth matches.
    scores_by_doc = collections.defaultdict(list)

    with open(args.query_results_manifest, "r") as in_list_fh:
        for line in in_list_fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            filepath = cleaned_line
            filename = os.path.basename(filepath)
            if not filename.endswith(".pickle"):
                _logger.info("Query results manifest: %r." % args.query_results_manifest)
                raise ValueError("Encountered a non-pickle file where only pickles were expected: %r." % filepath)

            node_id = filename.split(".pickle")[0]

            with open(filepath, "rb") as fh:
                unpickler = pickle.Unpickler(fh)
                results = unpickler.load()
                for (score, doc_name) in results:
                    #Only use non-0 scores.  A threshold of 0 does not make sense.
                    if score == 0.0:
                        continue
                    ground_truth_presence = gtdict.get((node_id, doc_name))
                    if ground_truth_presence == True:
                        scores_by_doc[doc_name].append(score)

    for doc_name in sorted(scores_by_doc.keys()):
        if args.avg:
            threshold_score = sum(scores_by_doc[doc_name]) / len(scores_by_doc[doc_name])
        elif args.max:
            threshold_score = max(scores_by_doc[doc_name])
        elif args.min:
            threshold_score = min(scores_by_doc[doc_name])
        searcher.doc_threshold[doc_name] = threshold_score

    searcher.save(args.out_pickle)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("ground_truth_db")
    parser.add_argument("vsm_pickle")
    parser.add_argument("query_results_manifest")
    parser.add_argument("out_pickle")

    whichscore_group = parser.add_mutually_exclusive_group(required=True)
    whichscore_group.add_argument("--avg", action="store_true", help="Pick average score.")
    whichscore_group.add_argument("--max", action="store_true", help="Pick maximum score.")
    whichscore_group.add_argument("--min", action="store_true", help="Pick minimum score.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
