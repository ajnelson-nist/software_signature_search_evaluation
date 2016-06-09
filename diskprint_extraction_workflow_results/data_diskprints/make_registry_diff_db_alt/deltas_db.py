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

"""
Export Postgres hive and regdelta tables to a portable SQLite file.
"""

__version__ = "0.3.4"

import argparse
import differ_db_library
import logging
import os
import sqlite3
import rx_make_database

_logger = logging.getLogger(os.path.basename(__file__))

#NOTE: Partial table.  Slice notes are intentionally not selected.
DELTADB_CREATE_SLICE = """
CREATE TABLE slice (
  osetid TEXT NOT NULL,
  appetid TEXT NOT NULL,
  sliceid INTEGER NOT NULL,
  predecessor_osetid TEXT,
  predecessor_appetid TEXT,
  predecessor_sliceid INTEGER,
  slicetype TEXT NOT NULL,
  slicestate TEXT NOT NULL
);
"""

DELTADB_CREATE_NAMEDSEQUENCEID = """
CREATE TABLE namedsequenceid (
  sequenceid INTEGER NOT NULL,
  sequencelabel TEXT NOT NULL
);
"""

DELTADB_CREATE_NAMEDSEQUENCE = """
CREATE TABLE namedsequence (
  sequencelabel TEXT NOT NULL,
  osetid TEXT NOT NULL,
  appetid TEXT NOT NULL,
  sliceid INTEGER NOT NULL,
  predecessor_osetid TEXT,
  predecessor_appetid TEXT,
  predecessor_sliceid INTEGER
);
"""

DELTADB_CREATE_CELL = """
CREATE TABLE cell (
  actionid NUMBER NOT NULL,
  actiontype TEXT NOT NULL
)
"""

DELTADB_CREATE_HIVE = """
CREATE TABLE hive (
  hiveid NUMBER NOT NULL,
  hivepath TEXT NOT NULL,
  sequenceid NUMBER NOT NULL
);
"""
DELTADB_INDEX_HIVE = """
CREATE INDEX idx_hive ON hive (hiveid);
"""

DELTADB_CREATE_REGDELTA = """
CREATE TABLE regdelta (
  sequenceid NUMBER NOT NULL,
  osetid TEXT NOT NULL,
  appetid TEXT NOT NULL,
  sliceid NUMBER NOT NULL,
  hiveid NUMBER NOT NULL,
  cellaction NUMBER NOT NULL,
  parentmtimebefore TEXT,
  parentmtimeafter TEXT,
  mtimebefore TEXT,
  mtimeafter TEXT,
  celltypebefore TEXT,
  celltypeafter TEXT,
  iskeybefore BOOLEAN NOT NULL,
  iskeyafter BOOLEAN NOT NULL,
  slicetype TEXT NOT NULL,
  basename TEXT,
  cellpath TEXT
);
"""
#AJN TODO Do I want slicetype in regdelta?

DELTADB_INDEX_REGDELTA = """
CREATE INDEX idx_regdelta ON regdelta (sequenceid, osetid, appetid, sliceid, hiveid, cellpath);
"""

def main():
    global args

    #Validate arguments
    if os.path.exists(args.output_db):
        raise ValueError("Output path must not already exist.")

    #Set up connections
    (inconn, incursor) = differ_db_library.db_conn_from_config_path(args.config)

    outconn = sqlite3.connect(args.output_db)
    outconn.isolation_level = "EXCLUSIVE"
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    #Construct output database
    outcursor.execute(DELTADB_CREATE_SLICE)
    outcursor.execute(DELTADB_CREATE_NAMEDSEQUENCE)
    outcursor.execute(DELTADB_CREATE_NAMEDSEQUENCEID)
    outcursor.execute(DELTADB_CREATE_CELL)
    outcursor.execute(DELTADB_CREATE_HIVE)
    outcursor.execute(DELTADB_CREATE_REGDELTA)

    #Populate output database
    for (table, query) in [
      ("slice", "SELECT osetid, appetid, sliceid, predecessor_osetid, predecessor_appetid, predecessor_sliceid, slicetype, slicestate FROM diskprint.slice;"),
      ("namedsequence", "SELECT * FROM diskprint.namedsequence;"),
      ("namedsequenceid", "SELECT * FROM diskprint.namedsequenceid;"),
      ("cell", "SELECT * FROM diskprint.cell;"),
      ("hive", "SELECT * FROM diskprint.hive ORDER BY hiveid, hivepath, sequenceid;"),

      #Note, psycopg2 by default loads all results into client RAM at once.  For this query, a named transaction will need to be implemented if the client machine has <10GB of RAM.
      #  https://stackoverflow.com/a/28343332
      #Also, using executemany() for this query did not provide an appreciable insertion rate difference.
      ("regdelta", "SELECT * FROM diskprint.regdelta ORDER BY sequenceid, osetid, appetid, sliceid, hiveid, cellpath;")
    ]:
        _logger.debug("Executing query: %r." % query)
        incursor.execute(query)
        last_row_no = 0
        for (row_no, row) in enumerate(incursor):
            #Note that psycopg2 rows, even with the dictionary generator, are Lists, not Dictionaries.  Make an output dictionary.
            outdict = dict()
            for key in row.keys():
                #Remove columns not relevant to cell-name analysis
                if key in ["datetime_ingested_to_postgres", "valuesha1after", "valuesha1before"]:
                    continue
                outdict[key] = row[key]
            rx_make_database.insert_db(outcursor, table, outdict)
            if row_no % 100000 == 0:
                _logger.debug("Committing record %d." % row_no)
                outconn.commit()
            last_row_no = row_no
        _logger.debug("Committed %d records." % last_row_no)

    outconn.commit()

    #Make indices after inserting data.  http://stackoverflow.com/questions/1711631/how-do-i-improve-the-performance-of-sqlite
    _logger.debug("Creating indices.")
    outcursor.execute(DELTADB_INDEX_HIVE)
    outcursor.execute(DELTADB_INDEX_REGDELTA)
    _logger.debug("Done.")
    outconn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Configuration file.", default="differ.cfg")
    parser.add_argument("-d", "--debug", help="Turn on debug-level logging.", action="store_true")
    parser.add_argument("output_db", help="Path to output SQLite database file.  Must not exist.")
    args = parser.parse_args()

    #Set up logging
    logging.basicConfig(
      format='%(asctime)s %(levelname)s: %(message)s',
      datefmt='%Y-%m-%dT%H:%M:%SZ',
      level=logging.DEBUG if args.debug else logging.INFO
    )

    main()
