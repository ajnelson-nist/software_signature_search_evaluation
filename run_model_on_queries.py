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

__version__ = "0.5.0"

import os
import logging
import sqlite3
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import TFIDFEngine

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("model_pickle")
    parser.add_argument("query_list_file")
    parser.add_argument("output_pickle_manifest")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    engine = TFIDFEngine.BasicTFIDFEngine()
    engine.load(args.model_pickle)

    output_dir = os.path.dirname(args.output_pickle_manifest)

    with open(args.query_list_file, "r") as in_list_fh:
      with open(args.output_pickle_manifest, "w") as out_list_fh:
        for line in in_list_fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            query_db_path = cleaned_line

            if not os.path.exists(query_db_path):
                raise ValueError("This path to a query db file does not exist: %r." % query_db_path)

            results = []
            with sqlite3.connect(query_db_path) as conn:
                _logger.debug("Running query: %r." % query_db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT term, tally FROM query;")
                query = []
                for row in cursor:
                    for x in range(row["tally"]):
                        query.append(row["term"])
        
                _logger.debug("len(query) = %d." % len(query))
                results = engine.query(query)
        
            query_basename = os.path.splitext(os.path.basename(query_db_path))[0]
            out_basename = query_basename + ".pickle"
            out_path = os.path.join(output_dir, out_basename)

            with open(out_path, "wb") as pickle_fh:
                pickler = pickle.Pickler(pickle_fh)
                pickler.dump(results)

                #Record successes
                print(out_path, file=out_list_fh)
