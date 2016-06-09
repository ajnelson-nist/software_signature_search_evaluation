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

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import hivexml_status_db_library as hsdl

def main():
    (outconn, outcursor) = hsdl.out_db_conn_cursor(args.out_db)

    for (dirpath, dirnames, filenames) in os.walk(args.dwf_node_results_root):
        #Do only a shallow walk.
        if dirpath != args.dwf_node_results_root:
            continue

        for dirname in dirnames:
            _logger.debug("Inspecting node %s." % dirname)

            node_dir_path = os.path.join(dirpath, dirname)
            os_type = "Win7"
            arch    = "64"

            hsdl.ingest_node_dir(node_dir_path, os_type, arch, outcursor)
            outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("dwf_node_results_root")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
