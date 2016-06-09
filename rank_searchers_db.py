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

__version__ = "0.6.2"

import pickle
import os
import logging
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

def parameter_tuple_from_path(filepath):
    #Extract Searcher parameters
    hierarchy =                 filepath.split("/")[1:-1]
    dataset =                   hierarchy[0].split("data_")[1]
    sequences =                 hierarchy[1].split("sequences_")[1]
    n_grams =                   hierarchy[2].split("n_grams_")[1]
    stop_list_n_gram_strategy = hierarchy[3].split("stop_list_n_gram_strategy_")[1]
    paths =                     hierarchy[4].split("paths_")[1]
    docs_by =                   hierarchy[5].split("docs_by_")[1]
    combinator =                hierarchy[6].split("combinator_")[1]
    stop_list =                 hierarchy[7].split("stop_list_")[1]
    versions =                  hierarchy[8].split("versions_")[1]
    score_selector =            hierarchy[9].split("score_selector_")[1]
    return (dataset, docs_by, versions, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, score_selector)

def searcher_id_from_tuple(docs_by, versions, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, score_selector):
    _1 = {
      "app": "A",
      "osapp": "B"
    }[docs_by]

    _2 = {
      "distinct": "C",
      "grouped": "D",
      None: "_"
    }[versions]

    _3 = {
      "raw": "E",
      "normalized": "F"
    }[paths]

    _4 = {
      "all": "WP",
      "1": "A1",
      "2": "A2",
      "3": "A3",
      "last1": "L1",
      "last2": "L2",
      "last3": "L3"
    }[n_grams]

    _5 = {
      "raw_filter": "G",
      "n_gram_blacklist": "H",
      "n_gram_threshold": "I"
    }[stop_list_n_gram_strategy]

    _6 = {
      "installclose": "J",
      "repeated": "K",
      "experiment1": "L"
    }[sequences]

    _7 = {
      "intersection": "M",
      "summation": "N",
      "sumint": "O"
    }[combinator]

    _8 = {
      "none": "P",
      "baseline": "Q",
      "bp": "R",
      "bpi": "S"
    }[stop_list]

    _9 = {
      "min": "T",
      "avg": "U",
      "max": "V",
      None: "_"
    }[score_selector]

    return "%s%s%s-%s-%s%s-%s%s%s" % (_1, _2, _3, _4, _5, _6, _7, _8, _9)

def vsm_id_from_tuple(sequences, n_grams, stop_list_n_gram_strategy, paths, docs_by, combinator, stop_list):
    return searcher_id_from_tuple(docs_by, None, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, None)

def main():
    conn = sqlite3.connect(args.output_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""\
CREATE TABLE searchers (
  searcher_id TEXT,
  vsm_id TEXT,
  accuracy NUMBER,
  num_test_nulls INTEGER,
  num_runs INTEGER,
  num_runs_in_ground_truth INTEGER,
  cond_pos INTEGER,
  cond_neg INTEGER,
  cond_null INTEGER,
  tp INTEGER,
  fp INTEGER,
  fn INTEGER,
  tn INTEGER,
  precision NUMBER,
  recall NUMBER,
  fpr NUMBER,
  f1 NUMBER,
  dataset TEXT,
  sequences TEXT,
  n_grams TEXT,
  stop_list_n_gram_strategy TEXT,
  paths TEXT,
  docs_by TEXT,
  combinator TEXT,
  stop_list TEXT,
  versions TEXT,
  score_selector TEXT,
  PRIMARY KEY(dataset, searcher_id)
);""")

    with open(args.measurement_manifest_txt, "r") as manifest_fh:
        for line in manifest_fh:
            cleaned_line = line.strip()
            if not cleaned_line.endswith(".pickle"):
                raise ValueError("Expecting only paths to pickles in the measurement manifest.  Encountered this line: %r." % cleaned_line)
            filepath = cleaned_line

            _logger.debug("Inspecting filepath: %r." % filepath)
            with open(filepath, "rb") as fh:
                unpickler = pickle.Unpickler(fh)
                tuples = unpickler.load()
                if len(tuples) == 0:
                    _logger.info("Skipping 0-length search results: %r." % filepath)
                    continue

                (dataset, docs_by, versions, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, score_selector) = parameter_tuple_from_path(filepath)
                searcher_id = searcher_id_from_tuple(docs_by, versions, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, score_selector)
                vsm_id = vsm_id_from_tuple(sequences, n_grams, stop_list_n_gram_strategy, paths, docs_by, combinator, stop_list)

                # (Test, Condition)
                truth_matrix = dict()
                for t in [True, False, None]:
                    for c in [True, False, None]:
                        truth_matrix[(t, c)] = 0

                #Track test records.
                #Also, aggregate records.
                for (node_id, doc_name, score, threshold, is_hit, should_be_hit) in tuples:
                    truth_matrix[(is_hit, should_be_hit)] += 1
                num_test_nulls = len([ t for t in tuples if t[4] is None ])
                num_non_null_conds = len([ t for t in tuples if not t[5] is None ])
                accuracy = (truth_matrix[(True, True)] + truth_matrix[(False, False)]) / float(num_non_null_conds)

                #NOTE: For precision and recall, if the measurement comes out to 0/0, it is convention to call that a score of 0 instead of infinity.  In particular, here, all-negative test responses means the Searcher is just completely wrong.
                if truth_matrix[(True, True)] + truth_matrix[(True, False)] > 0:
                    precision = ( 1.0 * truth_matrix[(True, True)] ) / ( truth_matrix[(True, True)] + truth_matrix[(True, False)] )
                else:
                    precision = 0.0

                if truth_matrix[(True, True)] + truth_matrix[(False, True)] > 0:
                    recall = ( 1.0 * truth_matrix[(True, True)] ) / ( truth_matrix[(True, True)] + truth_matrix[(False, True)] )
                else:
                    recall = 0.0

                if truth_matrix[(True, True)] + truth_matrix[(False, True)] + truth_matrix[(True, False)] > 0:
                    f1 = ( 2.0 * truth_matrix[(True, True)] ) / ( 2*truth_matrix[(True, True)] + truth_matrix[(False, True)] + truth_matrix[(True, False)] )
                else:
                    f1 = 0.0

                fpr = ( 1.0 * truth_matrix[(True, False)] ) / ( truth_matrix[(True, False)] + truth_matrix[(False, False)] )

                searchers_columns = (
                  searcher_id,
                  vsm_id,
                  accuracy,
                  num_test_nulls,
                  sum(truth_matrix.values()),
                  sum(truth_matrix.values()) - (truth_matrix[(True,None)] + truth_matrix[(False,None)]),
                  truth_matrix[(True,True)] + truth_matrix[(False,True)],
                  truth_matrix[(True,False)] + truth_matrix[(False,False)],
                  truth_matrix[(True,None)] + truth_matrix[(False,None)],
                  truth_matrix[(True,True)],
                  truth_matrix[(True,False)],
                  truth_matrix[(False,True)],
                  truth_matrix[(False,False)],
                  precision,
                  recall,
                  fpr,
                  f1,
                  dataset,
                  sequences,
                  n_grams,
                  stop_list_n_gram_strategy,
                  paths,
                  docs_by,
                  combinator,
                  stop_list,
                  versions,
                  score_selector
                )
                cursor.execute("INSERT INTO searchers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);", searchers_columns)

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
