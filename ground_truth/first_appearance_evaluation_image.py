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

__version__ = "0.1.0"

import sqlite3

def main():
    conn = sqlite3.connect(args.ground_truth_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("ATTACH DATABASE '%s' AS ep;" % args.etid_to_productname_db)

    cursor.execute("SELECT * FROM ground_truth_positive;")
    last_application_phase = None
    appearances = []
    for row in cursor:
        #E.g.:
        #  experiment1-2|15485-1/Install
        state_id = row["node_id"]
        state_number = int(state_id.split("-")[1])
        doc_name_parts = row["doc_name"].split("/")
        if len(doc_name_parts) == 2:
            osetid = None
        else:
            osetid = doc_name_parts[0]
        appetid = doc_name_parts[-2]
        ir = {
          "Install": "Install",
          "Close": "Run",
          "Function": "Run"
        }[doc_name_parts[-1]]
        #(Above this line is pretty much exactly as in tablify_evaluation_ground_truth.py.)

        current_application_phase = (appetid, ir)
        if current_application_phase == last_application_phase:
            continue
        last_application_phase = current_application_phase
        appearances.append((appetid, ir, state_number))

    #Look up names
    anno_appearances = []
    for (appetid, ir, state_number) in appearances:
        cursor.execute("SELECT * FROM ep.etid_to_productname WHERE ETID = ?;", (appetid,))
        row = cursor.fetchone()
        anno_appearances.append((row["ProductName"], row["Version"], ir, state_number))

    with open(args.out_file, "w") as fh:
        for row in anno_appearances:
            fh.write("%s & %s & %s & %d \\\\\n" % row)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("etid_to_productname_db")
    parser.add_argument("ground_truth_db")
    parser.add_argument("out_format", choices=["tex"])
    parser.add_argument("out_file")
    args = parser.parse_args()

    main()

#CREATE TABLE etid_to_productname (ETID STRING, ProductName STRING, Version STRING, PRIMARY KEY (ETID));
#CREATE TABLE ground_truth_positive (node_id TEXT, doc_name TEXT);
