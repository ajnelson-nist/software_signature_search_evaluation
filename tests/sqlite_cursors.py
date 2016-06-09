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
Verify that a connection made in one cursor is visible to another.
"""

import sqlite3
import logging

def main():
    conn = sqlite3.connect("sqlite_cursors_tmp3.db")
    cursor1 = conn.cursor()
    cursor2 = conn.cursor()

    cursor1.execute("ATTACH DATABASE 'sqlite_cursors_tmp1.db' AS t1;")

    cursor1.execute("SELECT * FROM t1.foo;")
    for row in cursor1:
        logging.info(row[0])
    cursor2.execute("SELECT * FROM t1.foo;")
    for row in cursor2:
        logging.info(row[0])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
