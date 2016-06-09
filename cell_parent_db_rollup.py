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
import collections

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer

import cell_parent_db

def main():
    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""\
CREATE TABLE cell_parent (
  cellpath TEXT PRIMARY KEY,
  basename TEXT,
  parentpath TEXT,
  tally INTEGER
);""")

    #For Reasons Unknown, the parent condensing takes much longer than expected if everything is dumped into temp_cell_parent.  Load everything into an in-memory tuple set instead.
    cell_parent_tuples = collections.Counter()
    _logger.info("Importing parent records into tuples set...")
    with open(args.db_manifest_txt, "r") as fh:
        for line in fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            _logger.debug("Connecting to database %r." % cleaned_line)
            cursor.execute("ATTACH DATABASE '%s' AS rx;" % cleaned_line)
            cursor.execute("""\
SELECT
  cellpath,
  basename,
  parentpath
FROM
  rx.cell_parent
;""")
            for row in cursor:
                cell_parent_tuples[(row["cellpath"], row["basename"], row["parentpath"])] += 1
            cursor.execute("DETACH DATABASE rx;")
    _logger.info("Done importing parent records into tuples set.")

    _logger.info("Inserting parent records into persistent table...")
    for key in sorted(cell_parent_tuples.keys()):
        rec = (key[0], key[1], key[2], cell_parent_tuples[key])
        try:
            cursor.execute("INSERT INTO cell_parent (cellpath, basename, parentpath, tally) VALUES (?,?,?,?);", rec)
        except sqlite3.IntegrityError:
            _logger.info("The failing record: %r." % (rec,))
            ecursor = conn.cursor()
            ecursor.execute("SELECT * FROM cell_parent WHERE cellpath = ?;", (key[0],))
            for erow in ecursor:
                td = {key:erow[key] for key in erow.keys()}
                _logger.info("Conflicting record: %r." % td)
            raise
    _logger.info("Done inserting parent records into persistent table.")

    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("db_manifest_txt")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
