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

__version__ = "0.1.1"

import pickle
import os
import logging
import sqlite3
import collections

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    conn = sqlite3.connect(args.output_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""\
CREATE TABLE thresholds (
  evaluation_pickle_path TEXT,
  doc_name TEXT,
  threshold NUMBER,
  cond_pos INTEGER,
  cond_neg INTEGER,
  tp INTEGER,
  fp INTEGER,
  fn INTEGER,
  tn INTEGER,
  precision NUMBER,
  recall NUMBER,
  f1 NUMBER,
  dataset TEXT,
  sequences TEXT
);""")

    #First key: (evaluation_pickle_path, doc_name)
    #Second key: (Test, Condition)
    #Value: Tally.
    aggregator = collections.defaultdict(lambda: collections.defaultdict(int))

    #First key: (evaluation_pickle_path, doc_name)
    #Value: Threshold.
    thresholds = dict()

    with open(args.measurement_manifest_txt, "r") as manifest_fh:
        for line in manifest_fh:
            cleaned_line = line.strip()
            if not cleaned_line.endswith(".pickle"):
                raise ValueError("Expecting only paths to pickles in the measurement manifest.  Encountered this line: %r." % cleaned_line)
            pickle_path = cleaned_line

            _logger.debug("Inspecting pickle path: %r." % pickle_path)
            with open(pickle_path, "rb") as pickle_fh:
                unpickler = pickle.Unpickler(pickle_fh)
                tuples = unpickler.load()
                if len(tuples) == 0:
                    _logger.info("Skipping 0-length search results: %r." % pickle_path)
                    continue
                for (node_id, doc_name, score, threshold, is_hit, should_be_hit) in tuples:
                    aggregator[(pickle_path, doc_name)][(is_hit, should_be_hit)] += 1
                    thresholds[(pickle_path, doc_name)] = threshold

    for (pickle_path, doc_name) in aggregator:
        truth_matrix = aggregator[(pickle_path, doc_name)]
        threshold = thresholds[(pickle_path, doc_name)]

        if truth_matrix[(True, True)] + truth_matrix[(True, False)] > 0:
            precision = truth_matrix[(True, True)] / ( truth_matrix[(True, True)] + truth_matrix[(True, False)] )
        else:
            precision = None

        if truth_matrix[(True, True)] + truth_matrix[(False, True)] > 0:
            recall = truth_matrix[(True, True)] / ( truth_matrix[(True, True)] + truth_matrix[(False, True)] )
        else:
            recall = None

        if truth_matrix[(True, True)] + truth_matrix[(False, True)] + truth_matrix[(True, False)] > 0:
            f1 = 2*truth_matrix[(True, True)] / ( 2*truth_matrix[(True, True)] + truth_matrix[(False, True)] + truth_matrix[(True, False)] )
        else:
            f1 = None

        #Extract model parameters
        hierarchy =          pickle_path.split("/")[1:-1]
        dataset =            hierarchy[0].split("data_")[1]
        sequences =          hierarchy[1].split("sequences_")[1]

        cursor.execute("""\
INSERT INTO thresholds(
  evaluation_pickle_path,
  doc_name,
  threshold,
  cond_pos,
  cond_neg,
  tp,
  fp,
  fn,
  tn,
  precision,
  recall,
  f1,
  dataset,
  sequences
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);""", (
          pickle_path,
          doc_name,
          threshold,
          truth_matrix[(True, True)] + truth_matrix[(False, True)],
          truth_matrix[(True, False)] + truth_matrix[(False, False)],
          truth_matrix[(True, True)],
          truth_matrix[(True, False)],
          truth_matrix[(False, True)],
          truth_matrix[(False, False)],
          precision,
          recall,
          f1,
          dataset,
          sequences
        ))

    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")

    parser.add_argument("measurement_manifest_txt")
    parser.add_argument("output_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
