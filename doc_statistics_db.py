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

__version__ = "0.6.0"

import pickle
import os
import logging
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import rank_searchers_db

def main():
    conn = sqlite3.connect(args.output_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""\
CREATE TABLE doc_statistics_id (
  vsm_id TEXT PRIMARY KEY,
  sequences TEXT,
  n_grams TEXT,
  stop_list_n_gram_strategy TEXT,
  paths TEXT,
  docs_by TEXT,
  combinator TEXT,
  stop_list TEXT
);""")
    cursor.execute("""\
CREATE TABLE doc_statistics_stat (
  vsm_id TEXT,
  doc_name TEXT,
  doc_len INTEGER
);""")

    def _generate_doc_statistics_rows(vsm_id, filepath):
        with sqlite3.connect(filepath) as inconn:
            inconn.row_factory = sqlite3.Row
            incursor = inconn.cursor()
            incursor.execute("SELECT * FROM doc_statistics;")
            for inrow in incursor:
                yield (vsm_id, inrow["doc_name"], inrow["doc_len"])

    with open(args.signature_statistics_manifest_txt, "r") as manifest_fh:
        for line in manifest_fh:
            cleaned_line = line.strip()
            if not cleaned_line.endswith(".db"):
                raise ValueError("Expecting only paths to databases in the signature statistics manifest.  Encountered this line: %r." % cleaned_line)
            filepath = cleaned_line
            _logger.debug("Inspecting filepath: %r." % filepath)

            #Extract model parameters
            hierarchy =                 filepath.split("/")[1:-1]
            sequences =                 hierarchy[0].split("sequences_")[1]
            n_grams =                   hierarchy[1].split("n_grams_")[1]
            stop_list_n_gram_strategy = hierarchy[2].split("stop_list_n_gram_strategy_")[1]
            paths =                     hierarchy[3].split("paths_")[1]
            docs_by =                   hierarchy[4].split("docs_by_")[1]
            combinator =                hierarchy[5].split("combinator_")[1]
            stop_list =                 hierarchy[6].split("stop_list_")[1]
            vsm_id = rank_searchers_db.vsm_id_from_tuple(sequences, n_grams, stop_list_n_gram_strategy, paths, docs_by, combinator, stop_list)

            doc_statistics_id_columns = (
              vsm_id,
              sequences,
              n_grams,
              stop_list_n_gram_strategy,
              paths,
              docs_by,
              combinator,
              stop_list
            )
            cursor.execute("INSERT INTO doc_statistics_id (vsm_id, sequences, n_grams, stop_list_n_gram_strategy, paths, docs_by, combinator, stop_list) VALUES (?,?,?,?,?,?,?,?);", doc_statistics_id_columns)

            cursor.executemany("INSERT INTO doc_statistics_stat VALUES (?,?,?);", _generate_doc_statistics_rows(vsm_id, filepath))
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")

    parser.add_argument("signature_statistics_manifest_txt")
    parser.add_argument("output_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
