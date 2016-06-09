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

import os
import logging
import sqlite3
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import rank_searchers_db

def main():
    conn = sqlite3.connect(args.output_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #Track document performance
    cursor.execute("""\
CREATE TABLE doc_performance (
  searcher_id TEXT,
  node_id TEXT,
  doc_name TEXT,
  score NUMBER,
  threshold NUMBER,
  is_hit BOOLEAN,
  should_be_hit BOOLEAN
);""")

    with open(args.measurement_manifest_txt, "r") as manifest_fh:
        for line in manifest_fh:
            cleaned_line = line.strip()
            if not cleaned_line.endswith(".pickle"):
                raise ValueError("Expecting only paths to pickles in the measurement manifest.  Encountered this line: %r." % cleaned_line)
            filepath = cleaned_line
            with open(filepath, "rb") as fh:
                unpickler = pickle.Unpickler(fh)
                tuples = unpickler.load()
                if len(tuples) == 0:
                    _logger.info("Skipping 0-length search results: %r." % filepath)
                    continue
                _logger.debug("Ingesting %r." % filepath)

                (dataset, docs_by, versions, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, score_selector) = rank_searchers_db.parameter_tuple_from_path(filepath)
                searcher_id = rank_searchers_db.searcher_id_from_tuple(docs_by, versions, paths, n_grams, stop_list_n_gram_strategy, sequences, combinator, stop_list, score_selector)

                def _generate_tuples():
                    for (node_id, doc_name, score, threshold, is_hit, should_be_hit) in tuples:
                        yield (
                          searcher_id,
                          node_id,
                          doc_name,
                          score,
                          threshold,
                          is_hit,
                          should_be_hit
                        )
                cursor.executemany("INSERT INTO doc_performance VALUES (?,?,?,?,?,?,?);", _generate_tuples())
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
