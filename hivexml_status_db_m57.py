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

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import m57_meta
import hivexml_status_db_library as hsdl

def main():
    machine_sequence_to_os_arch = {
      "charlie": ("XP", "32"),
      "jo-oldComputer": ("XP", "32"),
      "jo-newComputer": ("XP", "32"),
      "pat": ("XP", "32"),
      "terry-smallDrive": ("Vista", "32"),
      "terry-bigDrive": ("Vista", "32")
    }

    (outconn, outcursor) = hsdl.out_db_conn_cursor(args.out_db)

    for machine_sequence in sorted(m57_meta.MACHINE_TAG_SEQUENCES.keys()):
        _logger.debug("Running through machine sequence %r." % machine_sequence)
        os_type = machine_sequence_to_os_arch[machine_sequence][0]
        arch    = machine_sequence_to_os_arch[machine_sequence][1]
        for node_id in m57_meta.MACHINE_TAG_SEQUENCES[machine_sequence]:
            _logger.debug("Ingesting node %r." % node_id)
            node_dir_path = os.path.join(args.dwf_node_results_root, node_id)
            hsdl.ingest_node_dir(node_dir_path, os_type, arch, outcursor)

            regxml_extractor_results_id = hsdl.node_dir_id(node_dir_path, outcursor)
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
