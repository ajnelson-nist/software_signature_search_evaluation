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
    conn = sqlite3.connect(args.input_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    with open(args.output_tex, "w") as fh:
        cursor.execute("SELECT * FROM fail_ratio_by_filename ORDER BY corpus, filename;")

        for row in cursor:
            fdict = { key:row[key] for key in row.keys() }
            fh.write("%(corpus)s & %(filename)s & %(success_tally)d & %(failure_tally)d \\\\\n" % fdict)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_db")
    parser.add_argument("output_tex")
    args = parser.parse_args()
    main()
