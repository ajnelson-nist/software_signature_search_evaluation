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

__version__ = "0.3.2"

import logging
import os
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer

SQL_CREATE_TEMP_CELL_PARENT = """\
CREATE TEMPORARY TABLE temp_cell_parent (
  cellpath TEXT,
  basename TEXT,
  parentpath TEXT
);"""

SQL_CREATE_CELL_PARENT = """\
CREATE TABLE cell_parent AS
  SELECT
    cellpath,
    basename,
    parentpath,
    COUNT(*) AS tally
  FROM
    temp_cell_parent
  GROUP BY
    cellpath,
    basename,
    parentpath
  ORDER BY
    cellpath
;"""

SQL_CREATE_CELL_PARENT_INDEX = "CREATE INDEX idx_cell_parent ON cell_parent(cellpath);"

def main():
    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    rcursor = conn.cursor()
    wcursor = conn.cursor()

    _logger.debug("Attaching Registry state database %r." % args.rss_db)
    wcursor.execute("ATTACH DATABASE '%s' AS rss;" % args.rss_db)

    #Try to reduce seek times
    wcursor.execute("PRAGMA cache_size = 786432;") #3/4 GiB
    wcursor.execute("PRAGMA rss.cache_size = 1048576;") #1 GiB

    _logger.debug("Populating all-parent-path table...")
    wcursor.execute(SQL_CREATE_TEMP_CELL_PARENT)
    rcursor.execute("""\
SELECT
  filename,
  cellname,
  basename,
  type
FROM
  rss.cell_analysis AS c,
  rss.hive_analysis AS h
WHERE
  c.hive_id = h.hive_id
;""")
    for row in rcursor:
        cellpath = row["cellname"]
        if args.normalize:
            cellpath = normalizer.normalize_path(row["filename"], cellpath)

        if row["type"] == "root":
            #Root cell has no parent.
            parentpath = None
            basename = cellpath[1:] #Trim leading backslash
        else:
            basename = row["basename"]
            if basename is None:
                raise ValueError("Existence assumption violated: Null basename for cellpath %r, hive %r." % (row["cellname"], row["filename"]))
            #Trim trailing backslash as well
            parentpath = cellpath[ 0 : -len(basename)-1 ]

        wcursor.execute("INSERT INTO temp_cell_parent(cellpath, basename, parentpath) VALUES (?,?,?);", (cellpath, basename, parentpath))
    _logger.debug("Done populating all-parent-path table.")

    _logger.debug("Sorting and counting cell parent metadata from temporary table...")
    wcursor.execute(SQL_CREATE_CELL_PARENT)

    _logger.debug("Done sorting and counting cell parent metadata from temporary table.")

    _logger.debug("Creating all-parent-path index...")
    wcursor.execute(SQL_CREATE_CELL_PARENT_INDEX)
    _logger.debug("Done creating all-parent-path index.")

    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("rss_db", help="Registry single-state database file.")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
