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
Takes a ground truth SQLite database and makes a new one, with all of the input records, plus whatever ETIDs correspond to different versions of the same application.
"""

__version__ = "0.2.0"

import logging
import os
import sqlite3
import collections

_logger = logging.getLogger(os.path.basename(__file__))

ETID_BUNDLES = {
  "firefox": ["7895-1", "14887-1", "15981-1"],
  "msoffice": ["10248-1", "14351-1", "7740-1"],
  "turbotax": ["6031-1", "15562-1"],
  "photoshopelements": ["13859-1", "15681-1"],
  "googlechrome": ["9647-1", "15137-1"]
}

def main():
    all_doc_names = set()
    with sqlite3.connect(args.doc_names_db) as names_conn:
       names_conn.row_factory = sqlite3.Row
       names_cursor = names_conn.cursor()
       names_cursor.execute("SELECT DISTINCT doc_name FROM ground_truth_positive;")
       for row in names_cursor:
           all_doc_names.add(row["doc_name"])

    out_conn = sqlite3.connect(args.out_db)
    out_conn.row_factory = sqlite3.Row
    out_cursor_write = out_conn.cursor()
    out_cursor_read = out_conn.cursor()

    out_cursor_write.execute("""\
ATTACH DATABASE '%s' AS original;\
""" % args.in_db)

    out_cursor_write.execute("""\
CREATE TEMPORARY TABLE ground_truth_positive_temp AS
  SELECT
    *
  FROM
    original.ground_truth_positive
;""")

    out_conn.commit()

    #Build document name bundles from ETID bundles and list of doc names in the ground truth.
    #Key: Old document name.
    #Value: List of new document names.
    doc_name_bundles = collections.defaultdict(set)
    original_doc_names = []
    out_cursor_read.execute("""\
SELECT DISTINCT
  doc_name
FROM
  original.ground_truth_positive
;""")
    for row in out_cursor_read:
        original_doc_names.append(row["doc_name"])
    _logger.debug("%d original document names." % len(original_doc_names))
    for doc_name in original_doc_names:
        doc_name_parts = doc_name.split("/")
        #The app ETID is the penultimate part
        doc_name_etid = doc_name_parts[-2]
        for bundle_label in sorted(ETID_BUNDLES.keys()):
            #_logger.debug("Checking bundle %r for ETID %r." % (bundle_label, doc_name_etid))
            if not doc_name_etid in ETID_BUNDLES[bundle_label]:
                continue
            for etid in sorted(ETID_BUNDLES[bundle_label]):
                #Make a copy of the list, mutate it, then make the new doc name
                #This makes duplicates, but that's fine, we can use DISTINCT later.
                new_doc_name_parts = [part for part in doc_name_parts]
                new_doc_name_parts[-2] = etid
                new_doc_name = "/".join(new_doc_name_parts)

                #Ensure we didn't just invent a document that will never be found.
                if not new_doc_name in all_doc_names:
                    continue

                doc_name_bundles[doc_name].add(new_doc_name)

    _logger.debug("Using these document bundles: %r." % doc_name_bundles)
    for original_doc_name in sorted(doc_name_bundles.keys()):
        out_cursor_read.execute("""\
SELECT
  *
FROM
  original.ground_truth_positive
WHERE
  doc_name = ?
;""", (original_doc_name,))
        for read_row in out_cursor_read:
            for new_doc_name in sorted(doc_name_bundles[original_doc_name]):
                node_id = read_row["node_id"]
                out_cursor_write.execute("""\
INSERT INTO ground_truth_positive_temp (node_id, doc_name) VALUES (?,?);\
""", (node_id, new_doc_name))

    #Remove duplicates
    out_cursor_write.execute("""\
CREATE TABLE ground_truth_positive AS
  SELECT DISTINCT
    *
  FROM
    ground_truth_positive_temp 
;""")

    out_cursor_write.execute("""\
DETACH DATABASE original;\
""")

    out_conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("doc_names_db", help="Ground truth database that has all possible document names.")
    parser.add_argument("in_db")
    parser.add_argument("out_db")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
