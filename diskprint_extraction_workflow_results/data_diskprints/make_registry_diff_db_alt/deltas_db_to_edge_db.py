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

__version__ = "0.1.1"

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import differ_func_library

def main():
    (predecessor_osetid, predecessor_appetid, predecessor_sliceid) = differ_func_library.split_node_id(args.predecessor_node_id)
    (osetid, appetid, sliceid) = differ_func_library.split_node_id(args.node_id)

    inconn = sqlite3.connect(args.deltas_db)
    inconn.row_factory = sqlite3.Row
    incursor = inconn.cursor()

    outconn = sqlite3.connect(args.out_db)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    subsetter_where_clause = """\
  ns.predecessor_osetid = "%s" AND
  ns.predecessor_appetid = "%s" AND
  ns.predecessor_sliceid = %d AND
  ns.osetid = "%s" AND
  ns.appetid = "%s" AND
  ns.sliceid = %d AND
""" % (predecessor_osetid, predecessor_appetid, predecessor_sliceid, osetid, appetid, sliceid)

    def _generate_hive_analysis():
        incursor.execute("""\
SELECT
  h.hivepath,
  h.hiveid
FROM
  namedsequence AS ns,
  namedsequenceid AS nsi,
  hive AS h
WHERE
  ns.sequencelabel NOT LIKE "printed-%%" AND
  %s
  ns.sequencelabel = nsi.sequencelabel AND
  nsi.sequenceid = h.sequenceid
;""" % subsetter_where_clause)
        for row in incursor:
            yield (row["hiveid"], row["hivepath"]) 
    outcursor.executemany("INSERT INTO hive_analysis(hive_id, filename) VALUES(?,?);", _generate_hive_analysis())
    outconn.commit()

    def _generate_cell_analysis():
        incursor.execute("""\
SELECT
  h.hiveid,
  rd.cellpath
FROM
  namedsequence AS ns,
  namedsequenceid AS nsi,
  regdelta AS rd,
  hive AS h,
  cell AS c
WHERE
  ns.sequencelabel NOT LIKE "printed-%%" AND
  %s
  ns.sequencelabel = nsi.sequencelabel AND
  nsi.sequenceid = rd.sequenceid AND
  rd.hiveid = h.hiveid AND
  rd.cellaction = c.actionid AND
  c.actiontype = "created"
;""" % subsetter_where_clause)
        for row in incursor:
            yield (row["hiveid"], row["cellpath"]) 
    outcursor.executemany("INSERT INTO cell_analysis(hive_id, cellname) VALUES(?,?);", _generate_cell_analysis())
    outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("deltas_db")
    parser.add_argument("predecessor_node_id")
    parser.add_argument("node_id")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
