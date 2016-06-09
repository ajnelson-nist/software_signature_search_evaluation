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
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import TFIDFEngine

def total_term_frequency(engine, term):
    retval = 0
    for doc in engine.tf:
        retval += engine.tf[doc].get(term, 0)
    return retval

def main():
    global args

    engine = TFIDFEngine.BasicTFIDFEngine()
    engine.load(args.input_pickle)

    outconn = sqlite3.connect(args.output_db)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    outcursor.execute("CREATE TEMPORARY TABLE temp_path_stop_list (cellpath TEXT);")
    outcursor.execute("CREATE TEMPORARY TABLE temp_term_stop_list (term TEXT);")
    outcursor.execute("CREATE TEMPORARY TABLE temp_term_threshold (term TEXT, tally INTEGER);")

    if args.n_gram_length is None:
        #None -> "all"; that is, paths are terms.
        for term in engine.df.keys():
            outcursor.execute("INSERT INTO temp_path_stop_list VALUES (?);", (term,))
            outcursor.execute("INSERT INTO temp_term_stop_list VALUES (?);", (term,))
            outcursor.execute("INSERT INTO temp_term_threshold VALUES (?,?);", (term, total_term_frequency(engine, term)))
    else:
        #The engine contains terms derived from paths.  No need to use the n_grammer module here, all that splitting work's already done.
        for term in engine.df.keys():
            outcursor.execute("INSERT INTO temp_term_stop_list VALUES (?);", (term,))
            outcursor.execute("INSERT INTO temp_term_threshold VALUES (?,?);", (term, total_term_frequency(engine, term)))

    _logger.debug("Sorting results out of temporary tables.")
    outcursor.execute("""
CREATE TABLE path_stop_list AS
  SELECT DISTINCT
    cellpath
  FROM
    temp_path_stop_list
  ORDER BY
    cellpath
;""")
    outcursor.execute("""
CREATE TABLE term_stop_list AS
  SELECT DISTINCT
    term
  FROM
    temp_term_stop_list
  ORDER BY
    term
;""")
    outcursor.execute("""
CREATE TABLE term_threshold AS
  SELECT
    term,
    tally
  FROM
    temp_term_threshold
  ORDER BY
    term
;""")
    _logger.debug("Done sorting.")
    _logger.debug("Creating indices.")
    outcursor.execute("CREATE INDEX idx_path_stop_list ON path_stop_list (cellpath);")
    outcursor.execute("CREATE INDEX idx_term_stop_list ON term_stop_list (term);")
    outcursor.execute("CREATE INDEX idx_term_threshold ON term_threshold (term);")
    _logger.debug("Done.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--last-n", action="store_true", help="Only use last n terms of query (n set by --n-gram-length).  In this module, this flag has no effect, but keeps the generated-files tree in line for the symmetric difference stop lists.")
    parser.add_argument("--n-gram-length", type=int)
    parser.add_argument("input_pickle")
    parser.add_argument("output_db")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
