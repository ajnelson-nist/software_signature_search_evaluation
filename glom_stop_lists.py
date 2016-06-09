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

__version__ = "0.2.1"

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    conn = sqlite3.connect(args.output_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("CREATE TEMPORARY TABLE temp_path_stop_list (cellpath TEXT);")
    cursor.execute("CREATE TEMPORARY TABLE temp_term_stop_list (term TEXT);")
    cursor.execute("CREATE TEMPORARY TABLE temp_term_threshold (term TEXT, tally INTEGER);")

    def _check_count(table_name):
        if args.debug:
            cursor.execute("SELECT COUNT(*) AS tally FROM %s;" % table_name)
            row = cursor.fetchone()
            _logger.debug("Records in %s: %d." % (table_name, row["tally"]))

    for input_db in args.input_db:
        _logger.debug("input_db = %r." % input_db)
        cursor.execute("ATTACH DATABASE '%s' AS indb;" % input_db)
        cursor.execute("INSERT INTO temp_path_stop_list SELECT cellpath FROM indb.path_stop_list;")
        _check_count("indb.path_stop_list")
        _check_count("temp_path_stop_list")
        cursor.execute("INSERT INTO temp_term_stop_list SELECT term FROM indb.term_stop_list;")
        _check_count("indb.term_stop_list")
        _check_count("temp_term_stop_list")
        cursor.execute("INSERT INTO temp_term_threshold SELECT term, tally FROM indb.term_threshold;")
        _check_count("indb.term_threshold")
        _check_count("temp_term_threshold")
        cursor.execute("DETACH DATABASE indb;")

    cursor.execute("CREATE TABLE path_stop_list (cellpath TEXT UNIQUE);")
    cursor.execute("CREATE TABLE term_stop_list (term TEXT UNIQUE);")
    cursor.execute("CREATE TABLE term_threshold (term TEXT UNIQUE, tally INTEGER);")

    _logger.debug("Glomming path_stop_list...")
    cursor.execute("""
INSERT INTO path_stop_list
  SELECT DISTINCT
    cellpath
  FROM
    temp_path_stop_list
  ORDER BY
    cellpath
;""")
    _check_count("path_stop_list")
    _logger.debug("Glomming term_stop_list...")
    cursor.execute("""
INSERT INTO term_stop_list
  SELECT DISTINCT
    term
  FROM
    temp_term_stop_list
  ORDER BY
    term
;""")
    _check_count("term_stop_list")
    _logger.debug("Glomming term_threshold...")
    cursor.execute("""
INSERT INTO term_threshold
  SELECT
    term,
    SUM(tally) AS tally
  FROM
    temp_term_threshold
  GROUP BY
    term
  ORDER BY
    term
;""")
    _check_count("term_threshold")
    _logger.debug("Done glomming.")

    _logger.debug("Creating indices.")
    cursor.execute("CREATE INDEX idx_path_stop_list ON path_stop_list (cellpath);")
    cursor.execute("CREATE INDEX idx_term_stop_list ON term_stop_list (term);")
    cursor.execute("CREATE INDEX idx_term_threshold ON term_threshold (term);")
    _logger.debug("Done.")
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("output_db")
    parser.add_argument("input_db", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
