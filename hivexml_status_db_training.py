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

__version__ = "0.3.1"

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import hivexml_status_db_library as hsdl

def main():
    etid_to_os_arch = {
      "11331-2": ("XP", "32"),
      "234-1": ("XP", "32"),
      "9480-1": ("Win7", "32"),
      "9480-2": ("Win7", "64"),
      "9544-1": ("Win7", "64"),
      "8504-1": ("Vista", "32"),
      "8504-2": ("Vista", "64"),
      "14694-1": ("Win8", "32"),
      "14694-2": ("Win8", "64")
    }

    (outconn, outcursor) = hsdl.out_db_conn_cursor(args.out_db)

    outcursor.execute("""\
CREATE TABLE diskprints_meta (
  node_results_id INTEGER,
  osetid TEXT,
  appetid TEXT,
  sliceid INTEGER
);""")
    outconn.commit()

    inconn = sqlite3.connect(args.namedsequence_db)
    inconn.row_factory = sqlite3.Row
    incursor = inconn.cursor()

    incursor.execute("""\
SELECT
  osetid,
  appetid,
  sliceid
FROM
  namedsequence
WHERE
  sequencelabel LIKE 'installclose-%'
ORDER BY
  osetid,
  appetid,
  sliceid
;""")
    for row in incursor:
        osetid = row["osetid"]
        appetid = row["appetid"]
        sliceid = row["sliceid"]

        node_id = "%s-%s-%d" % (osetid, appetid, sliceid)

        _logger.debug("Inspecting node %r." % node_id)

        node_dir_path = os.path.join(args.diskprint_results_dir, "by_node", node_id)

        os_type = etid_to_os_arch[osetid][0]
        arch    = etid_to_os_arch[osetid][1]
        hsdl.ingest_node_dir(node_dir_path, os_type, arch, outcursor)
        node_results_id = hsdl.node_dir_id(node_dir_path, outcursor)
        outcursor.execute("INSERT INTO diskprints_meta (node_results_id, osetid, appetid, sliceid) VALUES (?,?,?,?);", (node_results_id, osetid, appetid, sliceid))
        outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("namedsequence_db")
    parser.add_argument("diskprint_results_dir")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
