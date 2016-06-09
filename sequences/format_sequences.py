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

_logger = logging.getLogger(os.path.basename(__file__))

import differ_func_library

def main():
    global args
    conn = sqlite3.connect(args.diskprint_export_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for root in args.sequences_root:
      _logger.debug("Walking sequences-root %r." % root)
      for (dirpath, dirnames, filenames) in os.walk(root):
        for filename in filenames:
            sequencelabel = filename
            _logger.debug("Creating records for sequence %r." % sequencelabel)

            with open(os.path.join(dirpath, filename), "r") as fh:
                predecessor_node_id_triple = None
                for line in fh:
                    cleaned_line = line.strip()
                    if cleaned_line == "":
                        continue

                    #_logger.debug("Getting node_id from line: %r." % cleaned_line)
                    node_id_triple = differ_func_library.split_node_id(cleaned_line)

                    #Insert record once we're past the first line of the file.
                    if not predecessor_node_id_triple is None:
                        (osetid, appetid, sliceid) = node_id_triple
                        (predecessor_osetid, predecessor_appetid, predecessor_sliceid) = predecessor_node_id_triple
                        cursor.execute("INSERT INTO namedsequence VALUES (?,?,?,?,?,?,?);", (
                          sequencelabel,
                          osetid,
                          appetid,
                          sliceid,
                          predecessor_osetid,
                          predecessor_appetid,
                          predecessor_sliceid
                        ))
                        conn.commit()

                    predecessor_node_id_triple = node_id_triple
                    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Enable debug printing", action="store_true")
    parser.add_argument("diskprint_export_db")
    parser.add_argument("sequences_root", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
