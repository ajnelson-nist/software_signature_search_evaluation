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

__version__ = "0.1.2"

import os
import logging
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import Objects

import normalizer

def main():
    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""\
CREATE TABLE recs (
  osetid TEXT NOT NULL,
  appetid TEXT NOT NULL,
  sliceid INTEGER NOT NULL,
  filename TEXT NOT NULL,
  hive_prefix TEXT NOT NULL
);\
""")

    #Build RE directory list from slice.db
    cursor.execute("ATTACH DATABASE '%s' AS slice;" % args.slice_db)
    cursor.execute("SELECT DISTINCT osetid, appetid, sliceid FROM slice.slice WHERE osetid <> '9544-1';")
    node_triples = []
    for row in cursor:
        node_triples.append((row["osetid"], row["appetid"], row["sliceid"]))
    cursor.execute("DETACH DATABASE slice;")

    #For each extraction.dfxml in an RE directory list
    for (osetid, appetid, sliceid) in sorted(node_triples):
        node_id = "%s-%s-%d" % (osetid, appetid, sliceid)
        extraction_dfxml_path = os.path.join(args.dwf_node_results_dir, node_id, "invoke_regxml_extractor.sh/extraction.dfxml")
        _logger.debug("extraction_dfxml_path = %r." % extraction_dfxml_path)

        if not os.path.exists(extraction_dfxml_path):
            _logger.warning("Skipping non-existent filepath: %r." % extraction_dfxml_path)
            continue

        #For each fileobject:
        for (event, obj) in Objects.iterparse(extraction_dfxml_path):
            if not isinstance(obj, Objects.FileObject):
                continue

            #Record node ID
            #Record node OS
            #Record hive filename
            #Record hive class (normalizer.py)
            hive_path = obj.original_fileobject.filename
            norm_prefix = normalizer.hive_path_to_prefix(hive_path)
            if norm_prefix is None:
                raise ValueError("File name has no associated prefix: %r." % obj.filename)
            cursor.execute("INSERT INTO recs(osetid, appetid, sliceid, filename, hive_prefix) VALUES (?,?,?,?,?);", (
              osetid,
              appetid,
              sliceid,
              hive_path,
              norm_prefix
            ))
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("slice_db")
    parser.add_argument("dwf_node_results_dir")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
