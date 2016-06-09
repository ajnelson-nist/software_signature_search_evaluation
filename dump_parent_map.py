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

import logging
import os
import sqlite3
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer
import n_grammer

def main():
    conn = sqlite3.connect(args.cell_parent_db)
    conn.row_factory = sqlite3.Row
    rcursor = conn.cursor()
    rcursor_aux = conn.cursor()
    wcursor = conn.cursor()

    ##Try to reduce seek times
    #wcursor.execute("PRAGMA cache_size = 2097152;") #2 GiB (page sizes default 1KiB)

    #Alias the database (just for the n_grammer module).
    rcursor_aux.execute("ATTACH DATABASE '%s' AS cp;" % args.cell_parent_db)

    _logger.debug("Running sorting query...")
    rcursor.execute("""\
SELECT
  cellpath,
  parentpath,
  basename
FROM
  cell_parent AS c
ORDER BY
  cellpath
;""")
    _logger.debug("Done with sorting query.")

    _logger.debug("Building cellpath-parent forest from cellpaths...")
    for (row_no, row) in enumerate(rcursor):
        n_grammer.ingest_into_parent_map(rcursor_aux, row["cellpath"])
    _logger.debug("Done building cellpath-parent forest.")

    with open(args.out_pickle, "wb") as fh:
        pickler = pickle.Pickler(fh)
        pickler.dump(n_grammer.parent_map)

    _logger.info("Number of auxiliary queries run for parent lookups: %d." % n_grammer.num_aux_queries_run)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")

    parser.add_argument("cell_parent_db", help="Database derived from cell_parent_db.py.")
    parser.add_argument("out_pickle")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
