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
Makes one of the files:
ground_truth/data_training/docs_by_{osapp,app}/versions_distinct/ground_truth_positive.db
"""

__version__ = "0.2.1"

import collections
import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import differ_func_library

def get_slice_type(cursor, node_id_triplet):
    cursor.execute("""
SELECT
  slicetype
FROM
  slice.slice
WHERE
  osetid = ? AND
  appetid = ? AND
  sliceid = ?
;""", node_id_triplet)
    rows = [row for row in cursor]
    if len(rows) == 0:
        _logger.debug("node_id_triplet = %r." % (node_id_triplet,))
    #_logger.debug("rows = %r." % rows)
    return rows[0]["slicetype"]

def doc_name_from_nit_and_st(node_id_triplet, slicetype):
    (osetid, appetid, sliceid) = node_id_triplet
    if args.by_osapp:
        doc_id = (osetid, appetid, slicetype)
    else:
        doc_id = (appetid, slicetype)
    doc_name = "/".join(doc_id)
    return doc_name
    
def main():
    #Key: Sequence label.
    #Value: List, tuples: (node ID, slice type).
    sequences = collections.defaultdict(list)

    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE ground_truth_positive (node_id TEXT, doc_name TEXT);")
    conn.commit()

    cursor.execute("ATTACH DATABASE %r AS namedsequence;" % args.namedsequence_db)
    cursor.execute("ATTACH DATABASE %r AS slice;" % args.slice_db)

    doc_names = set()

    #Build a dictionary of the sequences to sample.
    cursor.execute("""
SELECT
  *
FROM
  namedsequence.namedsequence
WHERE
  sequencelabel LIKE 'installclose-%'
ORDER BY
  sequencelabel,
  sliceid
;""")
    rows = [row for row in cursor]
    for row in rows:
        if len(sequences[row["sequencelabel"]]) == 0:
            predecessor_node_id = None
            predecessor_node_id = "%(predecessor_osetid)s-%(predecessor_appetid)s-%(predecessor_sliceid)d" % row
            predecessor_slicetype = get_slice_type(cursor, (row["predecessor_osetid"], row["predecessor_appetid"], row["predecessor_sliceid"]))
            sequences[row["sequencelabel"]].append((predecessor_node_id, predecessor_slicetype))
        node_id = "%(osetid)s-%(appetid)s-%(sliceid)d" % row
        slicetype = get_slice_type(cursor, (row["osetid"], row["appetid"], row["sliceid"]))
        sequences[row["sequencelabel"]].append((node_id, slicetype))

        #Note that the baseline image is not given a document.
        doc_name = doc_name_from_nit_and_st((row["osetid"], row["appetid"], row["sliceid"]), slicetype)
        doc_names.add(doc_name)


    _logger.debug(repr(sequences))

    for sequence in sorted(sequences.keys()):
        #Reset for each sequence.
        ground_truth_positive_documents = set()
        for (node_id, slicetype) in sequences[sequence]:
            _logger.debug("node_id = %r." % node_id)
            (osetid, appetid, sliceid) = differ_func_library.split_node_id(node_id)
            maybe_doc_name = doc_name_from_nit_and_st((osetid, appetid, sliceid), slicetype)
            #Accumulate document ID's - the signature has been present in the sequence.
            if maybe_doc_name in doc_names:
                ground_truth_positive_documents.add(maybe_doc_name)

            for doc_name in ground_truth_positive_documents:
                _logger.debug("doc_name = %r." % (doc_name,))
                cursor.execute("INSERT INTO ground_truth_positive(node_id, doc_name) VALUES (?,?);", (node_id, doc_name))

    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("namedsequence_db")
    parser.add_argument("slice_db")
    parser.add_argument("out_db")

    docsby_group = parser.add_mutually_exclusive_group(required=True)
    docsby_group.add_argument("--by-app", action="store_true", help="Group document names by AppETID and SliceType.")
    docsby_group.add_argument("--by-osapp", action="store_true", help="Group document names by OSETID, AppETID, and SliceType.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
