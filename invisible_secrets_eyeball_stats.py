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

import os
import logging
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    meta_conn = sqlite3.connect(":memory:")
    meta_conn.row_factory = sqlite3.Row
    meta_cursor = meta_conn.cursor()
    meta_cursor.execute("ATTACH DATABASE '%s' AS namedsequence;" % args.sequence_db)
    meta_cursor.execute("ATTACH DATABASE '%s' AS slice;" % args.slice_db)

    meta_cursor.execute("""\
SELECT
  ns.*,
  s.slicetype
FROM
  namedsequence.namedsequence AS ns,
  slice.slice AS s
WHERE
  ns.osetid = s.osetid AND
  ns.appetid = s.appetid AND
  ns.sliceid = s.sliceid AND
  ns.appetid = '15489-1' AND
  ns.sequencelabel LIKE 'installclose-%'
;""")

    for meta_row in meta_cursor:
        node_id = "%(osetid)s-%(appetid)s-%(sliceid)d" % meta_row
        predecessor_node_id = "%(predecessor_osetid)s-%(predecessor_appetid)s-%(predecessor_sliceid)d" % meta_row
        new_cell_db_path = os.path.join(args.dwf_results_root, "by_edge", predecessor_node_id, node_id, "make_registry_diff_db.sh", "registry_new_cellnames.db")
        with sqlite3.connect(new_cell_db_path) as new_cell_db_conn:
            new_cell_db_conn.row_factory = sqlite3.Row
            new_cell_db_cursor = new_cell_db_conn.cursor()
            new_cell_db_cursor.execute("""\
SELECT
  COUNT(*) AS tally
FROM
  cell_analysis
;""")
            for new_cell_db_row in new_cell_db_cursor:
                _logger.info("\t".join([
                  meta_row["sequencelabel"],
                  predecessor_node_id,
                  node_id,
                  meta_row["slicetype"],
                  str(new_cell_db_row["tally"])
                ]))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence_db")
    parser.add_argument("slice_db")
    parser.add_argument("dwf_results_root")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main()
