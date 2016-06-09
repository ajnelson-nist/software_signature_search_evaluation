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

import os
import logging
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("ATTACH DATABASE '%s' AS etp;" % args.productname_db)
    cursor.execute("ATTACH DATABASE '%s' AS slice;" % args.slice_db)

    unlabeled_etids = set()
    for etid in ["osetid", "appetid"]:
        _logger.debug("Checking %ss." % etid)
        cursor.execute("""\
SELECT DISTINCT
  %s
FROM
  slice.slice
WHERE
  %s NOT IN (
    SELECT DISTINCT
      %s
    FROM
      etp.etid_to_productname
  )
;""" % (etid, etid, etid))
        for row in cursor:
            unlabeled_etids.add(row[etid])
    if len(unlabeled_etids) > 0:
        _logger.error("The Diskprint database has a print for these ETIDs, but the label database doesn't have that ETID.")
        for etid in sorted(unlabeled_etids):
            _logger.error("* %s" % slicerow["etid"])
        raise ValueError("%d lookups failed." % len(unlabeled_etids))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("productname_db", help="SQLite database mapping ETID's to ProductNames.")
    parser.add_argument("slice_db")
    parser.add_argument("--debug", help="Turn on debug-level logging.", action="store_true")
    args = parser.parse_args()

    #Set up logging
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
