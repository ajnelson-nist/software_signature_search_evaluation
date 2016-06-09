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
import collections

_logger = logging.getLogger(os.path.basename(__file__))

short_names = {
  "15485-1": "Keylogger",
  "14417-1": "Wireshark",
  "15150-1": "HxD",
  "15489-1": "Inv. Secs.",
  "14887-1": "Firefox",
  "15487-1": "Python",
  "7959-1": "Thunderbird",
  "15488-1": "TrueCrypt",
  "14351-1": "Office",
  "15149-1": "Winrar",
  "15142-1": "SDelete",
  "14782-1": "Winzip",
  "15146-1": "Eraser",
}

def main():
    conn = sqlite3.connect(args.ground_truth_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    long_names = dict()
    with sqlite3.connect(args.etid_to_productname_db) as labelconn:
        labelconn.row_factory = sqlite3.Row
        labelcursor = labelconn.cursor()
        labelcursor.execute("SELECT ETID, ProductName FROM etid_to_productname;")
        for row in labelcursor:
            long_names[row["ETID"]] = row["ProductName"]

    all_state_columns = [x for x in range(1,20+1)]

    #Key: (osetid, appetid, install/run)
    #Value: dict
    #  Key: state_column
    #  Value: Boolean
    rotated = collections.defaultdict(dict)
    cursor.execute("SELECT * FROM ground_truth WHERE present = 1;")
    for row in cursor:
        #E.g.:
        #  experiment1-2|15485-1/Install
        state_id = row["node_id"]
        state_column = int(state_id.split("-")[1])
        doc_name_parts = row["doc_name"].split("/")
        if len(doc_name_parts) == 2:
            osetid = None
        else:
            osetid = doc_name_parts[0]
        appetid = doc_name_parts[-2]
        ir = {
          "Install": "I",
          "Close": "R",
          "Function": "R"
        }[doc_name_parts[-1]]
        rotated[(osetid, appetid, ir)][state_column] = True

    #Sort.

    #Key: As with the rotated dict.
    #Value: Count of Trues in the nested dictionary in rotated[key].
    row_true_tallies = dict()
    for key in rotated:
        row_true_tallies[key] = 0
        for state_column in rotated[key]:
            if rotated[key][state_column]:
                row_true_tallies[key] += 1
    row_order = [ (row_true_tallies[key], key) for key in row_true_tallies ]
    with open(args.out_file, "w") as fh:
        for (tally, (osetid, appetid, ir)) in sorted(row_order, reverse=True):
            key = (osetid, appetid, ir)
            row_contents = []
            row_contents.append("" if osetid is None else osetid)
            if args.use_short_names:
                try:
                    row_contents.append(short_names[appetid])
                except:
                    _logger.info("No short name provided for application %r (ETID %r)." % (long_names[appetid], appetid))
                    raise
            else:
                row_contents.append(long_names[appetid])
            row_contents.append(ir)
            for state_column in all_state_columns:
                row_contents.append("X" if rotated[key].get(state_column) == True else "")
            fh.write(" & ".join(row_contents))
            fh.write(" \\\\\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--use-short-names", action="store_true")
    parser.add_argument("etid_to_productname_db")
    parser.add_argument("ground_truth_db")
    parser.add_argument("out_format", choices=["tex"])
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
