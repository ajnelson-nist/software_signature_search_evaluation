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

import logging
import os
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    global args

    #Count Registry stuff
    reg_count = 0
    _logger.debug("Begin SQLite count of %r." % args.rxdb_path)
    conn = sqlite3.connect(args.rxdb_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cell_analysis;")
    for row in cursor:
        reg_count = row[0]

    with open(args.text_output, "w") as fh:
        fh.write(str(reg_count))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("rxdb_path")
    parser.add_argument("text_output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
