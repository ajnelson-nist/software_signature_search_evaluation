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
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import application_appearances as aa
import m57_meta

def main():
    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE ground_truth_positive (node_id TEXT, doc_name TEXT);")
    conn.commit()

    #machine_tag: Name of machine sequence (e.g. "charlie", "jo-oldComputer")
    for machine_tag in sorted(m57_meta.MACHINE_TAG_SEQUENCES.keys()):
        sequence = m57_meta.MACHINE_TAG_SEQUENCES[machine_tag]
        #Accumulate docs
        docs = set()
        for node_id in sequence:
            for m57_doc_name in sorted(aa.appearances.keys()):
                if m57_doc_name.startswith("m57-"):
                    _logger.info("Placeholder signature name found, should be replaced with Diskprint signature name: %r." % m57_doc_name)
                    continue

                #Determine diskprint document name from document name hard-coded in the application appearances dictionary.
                if args.docs_by == "app":
                    m57_doc_name_parts = m57_doc_name.split("/")
                    diskprint_doc_name = "/".join([m57_doc_name_parts[-2], m57_doc_name_parts[-1]])
                elif args.docs_by == "osapp":
                    diskprint_doc_name = m57_doc_name
                else:
                    raise NotImplementedError("Document grouping not implemented: %r." % args.docs_by)

                #Add diskprint document name to the set of documents present in this node of the machine state sequence.
                if machine_tag in aa.appearances[m57_doc_name]:
                    #First element of pair is the "On" toggle, second is the "Off" indicating app removal.
                    if aa.appearances[m57_doc_name][machine_tag][0] == node_id:
                        docs.add(diskprint_doc_name)
                    elif aa.appearances[m57_doc_name][machine_tag][1] == node_id:
                        docs.remove(diskprint_doc_name)
            for doc in docs:
                _logger.debug("node_id = %r." % node_id)
                _logger.debug("doc = %r." % doc)
                cursor.execute("INSERT INTO ground_truth_positive VALUES (?,?);", (node_id, doc))
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("docs_by", choices=["app","osapp"])
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
