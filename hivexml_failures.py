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

"""
This script reports failures due to hivexml, which include hivexml failing *and* xmllint failing to read hivexml output (e.g. from output of badly formatted binary data).
"""

import os
import logging
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer

def main():
    outconn = sqlite3.connect(args.output_db)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    outcursor.execute("""\
CREATE TABLE failures_by_filename (
  id INTEGER PRIMARY KEY,
  filename STRING NOT NULL,
  prefix STRING,
  corpus STRING NOT NULL
);""")

    outcursor.execute("""\
CREATE TABLE successes_by_filename (
  filename STRING NOT NULL,
  corpus STRING NOT NULL,
  tally INTEGER NOT NULL,
  PRIMARY KEY (corpus, filename)
);""")

    for input_db in args.input_db:
        with sqlite3.connect(input_db) as inconn:
            corpus = input_db.split("data_")[1].split("/")[0]

            inconn.row_factory = sqlite3.Row
            incursor = inconn.cursor()

            #Assemble set of files that failed hivexml or xmllint.
            incursor.execute("SELECT * FROM hive_survival WHERE hivexml_exit_status <> 0 OR xmllint_exit_status <> 0;")
            for row in incursor:
                outcursor.execute("INSERT INTO failures_by_filename (filename, prefix, corpus) VALUES (?,?,?);", (
                  row["filename"],
                  normalizer.hive_path_to_prefix(row["filename"]),
                  corpus
                ))

            #Assemble the gauntlet survivors.
            incursor.execute("SELECT filename, COUNT(*) AS tally FROM hive_survival WHERE hivexml_exit_status = 0 AND xmllint_exit_status = 0 GROUP BY filename;")
            for row in incursor:
                outcursor.execute("INSERT INTO successes_by_filename (filename, corpus, tally) VALUES (?,?,?);", (
                  row["filename"],
                  corpus,
                  row["tally"]
                ))

    outcursor.execute("""\
CREATE TABLE fail_ratio_by_filename (
  filename STRING NOT NULL,
  prefix STRING,
  corpus STRING NOT NULL,
  success_tally INTEGER NOT NULL,
  failure_tally INTEGER NOT NULL
);""")

    outcursor_aux1 = outconn.cursor()
    outcursor_aux2 = outconn.cursor()
    outcursor_aux1.execute("SELECT corpus, prefix, filename, COUNT(*) AS tally FROM failures_by_filename GROUP BY corpus, prefix, filename;")
    for f_row in outcursor_aux1:
        outcursor_aux2.execute("SELECT * FROM successes_by_filename WHERE filename = ? AND corpus = ?;", (f_row["filename"], f_row["corpus"]))

        #If there aren't successes, this remains 0.
        success_tally = 0
        for s_row in outcursor_aux2:
            success_tally = s_row["tally"]

        outcursor.execute("INSERT INTO fail_ratio_by_filename (filename, prefix, corpus, success_tally, failure_tally) VALUES (?,?,?,?,?);", (
          f_row["filename"],
          f_row["prefix"],
          f_row["corpus"],
          success_tally,
          f_row["tally"]
        ))
    outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("output_db")
    parser.add_argument("input_db", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
