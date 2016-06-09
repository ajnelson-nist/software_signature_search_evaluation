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

__version__ = "0.3.0"

import collections
import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    conn = sqlite3.connect(args.namedsequence_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    labelconn = sqlite3.connect(args.etid_to_productname_db)
    labelconn.row_factory = sqlite3.Row
    labelcursor = labelconn.cursor()

    sequencelabels = set()
    cursor.execute("SELECT * FROM namedsequence WHERE sequencelabel LIKE 'installclose-%';")
    for row in cursor:
        sequencelabels.add(row["sequencelabel"])

    os_format = {
      "234-1": "XP/32",
      "8504-1": "V/32",
      "8504-2": "V/64",
      "9480-1": "7/32",
      "9480-2": "7/64",
      "14694-1": "8/32"
    }
    os_order = ["XP/32", "V/32", "V/64", "7/32", "7/64", "8/32"]
    assert set(os_format.values()) == set(os_order)
    if len(os_order) != 6:
        raise ValueError("The analysis document expects there to be six OS columns.  Please adjust the document and then this hard-coded test in this program.")

    #Key: (Application name, application version) pair.
    #Value: Dictionary.
    #  Key: Formatted OS ETID.
    #  Value:  Tally of instances of that app on that OS.
    
    apposmatrix = collections.defaultdict(lambda:collections.defaultdict(int))
    for sequencelabel in sorted(sequencelabels):
        labelparts = sequencelabel.split("-")
        appetid = "-".join(labelparts[-3:-1])
        osetid = "-".join(labelparts[-5:-3])
        os_formatted = os_format[osetid]
        labelcursor.execute("SELECT * FROM etid_to_productname WHERE ETID = ?;", (appetid,))
        row = labelcursor.fetchone()
        app_label = row["ProductName"]
        app_version = str(row["Version"])
        #_logger.debug("%r -> %r (%r), %r (%r)" % (sequencelabel, osetid, os_formatted, appetid, app_formatted))
        apposmatrix[(app_label, app_version)][os_formatted] += 1
    #_logger.debug(apposmatrix)

    #The LaTeX header is just typed into the Registry analysis document.
    if args.latex:
      with open(args.out_file, "w") as fh:
        num_skipped = 0
        num_printed = 0
        for (app_label, app_version) in sorted(apposmatrix.keys()):
            if not args.skip is None:
                if num_skipped < args.skip:
                    num_skipped += 1
                    continue

            fh.write("%s & %s" % (app_label, app_version))
            for os in os_order:
                fh.write(" & %d" % apposmatrix[(app_label, app_version)][os])
            fh.write(" \\\\\n")

            num_printed += 1
            if not args.count is None:
                if num_printed >= args.count:
                    break
    else:
      with open(args.out_file, "w") as fh:
        fh.write("""\
<table>
  <thead>
    <tr>
      <th rowspan="2">Application</th>
      <th rowspan="2">Version</th>
      <th colspan="%d">Count of prints on OS & architecture</th>
    </tr>
    <tr>
""" % len(os_order))
        for os in os_order:
            fh.write("""\
      <th>%s</th>
""" % os)
        fh.write("""\
    </tr>
  </thead>
  <tfoot></tfoot>
  <tbody>
""")
        for (app_label, app_version) in sorted(apposmatrix.keys()):
            fh.write("""\
    <tr>
      <td>%s</td>
      <td>%s</td>
""" % (app_label, app_version))
            for os in os_order:
                fh.write("""\
      <td>%d</td>
""" % apposmatrix[(app_label, app_version)][os])
            fh.write("""\
    </tr>
""")
        fh.write("""\
  </tbody>
</table>
""")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--latex", action="store_true")
    parser.add_argument("--count", type=int, help="Only put N records into table.")
    parser.add_argument("--skip", type=int, help="Skip the first N results.")
    parser.add_argument("namedsequence_db")
    parser.add_argument("etid_to_productname_db")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
