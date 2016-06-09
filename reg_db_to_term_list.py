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

__version__ = "0.11.0"

import logging
import os
import sqlite3
import collections
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer
import vsm_set_theory_ops

def main():
    path_to_n_grams = dict()
    _logger.debug("Loading cell path n-gram dictionary...")
    with open(args.n_gram_derivation_pickle, "rb") as ng_fh:
        unpickler = pickle.Unpickler(ng_fh)
        path_to_n_grams = unpickler.load()
    _logger.debug("Done loading cell path n-gram dictionary.")

    conn = sqlite3.connect(args.out_db)
    #conn.isolation_level = "EXCLUSIVE" #Don't do this.  It locks attached databases too.
    conn.row_factory = sqlite3.Row
    rcursor = conn.cursor()
    wcursor = conn.cursor()

    _logger.debug("Attaching Registry state database %r." % args.rss_db)
    wcursor.execute("ATTACH DATABASE '%s' AS rss;" % args.rss_db)

    ##Try to reduce seek times
    #wcursor.execute("PRAGMA cache_size = 2097152;") #2 GiB (page sizes default 1KiB)
    #wcursor.execute("PRAGMA rss.cache_size = 1048576;") #1 GiB

    #A temporary table helps sort cells for faster query construction later
    wcursor.execute("CREATE TEMPORARY TABLE temp_paths (path_id INTEGER PRIMARY KEY, cellpath TEXT);")
    wcursor.execute("CREATE TABLE paths (path_id INTEGER PRIMARY KEY, cellpath TEXT);")

    #The 'terms.term' field is intentionally not distinct.
    wcursor.execute("CREATE TEMPORARY TABLE temp_terms (term_id INTEGER PRIMARY KEY, source_path_id INTEGER, term TEXT);")
    wcursor.execute("CREATE TABLE terms (term_id INTEGER PRIMARY KEY, source_path_id INTEGER, term TEXT);")

    _logger.debug("Extracting cell paths from Registry state database.")
    def _generate_paths():
        rcursor.execute("""\
SELECT
  filename,
  cellname
FROM
  rss.hive_analysis AS ha,
  rss.cell_analysis AS ca
WHERE
  ha.hive_id = ca.hive_id
;""")
        for row in rcursor:
            if args.normalize:
                query_path = normalizer.normalize_path(row["filename"], row["cellname"])
            else:
                query_path = row["cellname"]
            yield (query_path,)

    wcursor.executemany("INSERT INTO temp_paths (cellpath) VALUES (?);", _generate_paths())

    _logger.debug("Inserted paths into temporary table.  Sorting into persistent table.")
    wcursor.execute("INSERT INTO paths (cellpath) SELECT cellpath FROM temp_paths ORDER BY cellpath;")
    _logger.debug("Inserted paths into persistent table.  Building index.")
    wcursor.execute("CREATE INDEX idx_paths ON paths(cellpath);")
    wcursor.execute("DROP TABLE temp_paths;")
    conn.commit()

    _logger.debug("Building n-gram set from all cellpaths.")
    def _generate_terms():
        rcursor.execute("""\
SELECT
  path_id,
  cellpath
FROM
  paths
;""")
        procced_row_count = 0
        for (row_no, row) in enumerate(rcursor):
            last_row_no = row_no
            derived_terms = path_to_n_grams[row["cellpath"]]

            for derived_term in derived_terms:
                yield (row["path_id"], derived_term)
    wcursor.executemany("INSERT INTO temp_terms (source_path_id, term) VALUES (?,?);", _generate_terms())

    _logger.debug("Built n-grams.  Sorting.")
    wcursor.execute("""\
INSERT INTO terms (source_path_id, term)
  SELECT
    source_path_id,
    term
  FROM
    temp_terms
  ORDER BY
    term
;""")
    _logger.debug("Sorted.  Building index.")
    wcursor.execute("CREATE INDEX idx_terms ON terms(term);")
    _logger.debug("Committing.")
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("n_gram_derivation_pickle", help="Pre-computed n-grams of Registry paths.")
    parser.add_argument("rss_db")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()

