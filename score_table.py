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

__version__ = "0.4.0"

import logging
import os
import pickle
import collections

import numpy as np
import pandas as pd

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    #Key: Node ID.
    #Value: [(score, doc_name)]
    node_similarity_results = dict()

    with open(args.pickle_manifest, "r") as manifest_fh:
        for line in manifest_fh:
            filepath = line.strip()
            filename = os.path.basename(filepath)
            if not filepath.endswith(".pickle"):
                _logger.warning("Encountered a non-pickle file in the input manifest %r: %r." % (args.pickle_manifest, filepath))
                continue
            node_id = filename.split(".pickle")[0]
            with open(filepath, "rb") as fh:
                unpickler = pickle.Unpickler(fh)
                node_similarity_results[node_id] = unpickler.load()
    #_logger.debug("node_similarity_results = %r." % node_similarity_results)

    #Example code:
    #http://stackoverflow.com/questions/19622407/2d-numpy-array-to-html-table

    node_ids_unsorted = set([ key for key in node_similarity_results.keys() ])
    node_ids_and_sort_key = []
    for node_id in node_ids_unsorted:
        integer_quintuple = tuple( map(int, node_id.split("-")) )
        #_logger.debug(repr(integer_quintuple))
        if args.only_firefox:
            node_parts = node_id.split("-")
            if not node_parts[2] in ["7895", "14887", "15981"]:
                continue
        if args.only_msoffice:
            node_parts = node_id.split("-")
            if not node_parts[2] in ["7740", "10248", "14351"]:
                continue
        node_ids_and_sort_key.append( (integer_quintuple, node_id) )
    #_logger.debug(sorted(node_ids_and_sort_key))
    node_ids = [ node_id for (key, node_id) in sorted(node_ids_and_sort_key) ]

    doc_names_unsorted = set([])
    doc_names_and_sort_key = []
    for node_id in node_similarity_results:
        for (score, doc_name) in node_similarity_results[node_id]:
            if args.only_firefox:
                name_parts = doc_name.split("/")
                if not name_parts[-2] in ["7895-1", "14887-1", "15981-1"]:
                    continue
            if args.only_msoffice:
                name_parts = doc_name.split("/")
                if not name_parts[-2] in ["7740-1", "10248-1", "14351-1"]:
                    continue
            doc_names_unsorted.add(doc_name)
    for doc_name in doc_names_unsorted:
        name_parts = doc_name.split("/")
        #There is either just the app ETID, or the os and app ETIDs
        numeric_parts = tuple(map(lambda x: [y for y in map(int, x.split("-"))], name_parts[:-1]))
        doc_name_key = ( numeric_parts, {"Install":0, "Close":1, "Function":1}[name_parts[-1]])
        doc_names_and_sort_key.append( (doc_name_key, doc_name) )
    doc_names = [ doc_name for (key, doc_name) in sorted(doc_names_and_sort_key) ]

    #_logger.debug("node_ids = %r." % node_ids)
    #_logger.debug("len(node_ids) = %r." % len(node_ids))
    #_logger.debug("doc_names = %r." % doc_names)
    #_logger.debug("len(doc_names) = %r." % len(doc_names))

    filled_table = collections.defaultdict(lambda: collections.defaultdict(float))
    for node_id in node_similarity_results:
        for (score, doc_name) in node_similarity_results[node_id]:
            filled_table[node_id][doc_name] = score

    ll = []
    for node_id in node_ids:
        ll.append([])
        for doc_name in doc_names:
            ll[-1].append(filled_table[node_id][doc_name])

    num = np.array(ll)
    df = pd.DataFrame(num, index=node_ids, columns=doc_names)
    #_logger.debug("dir(df) = %r." % dir(df))

    with open(args.output_html, "w") as fh:
        html = df.to_html()
        fh.write(html)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")

    only_app_group = parser.add_mutually_exclusive_group(required=False)
    only_app_group.add_argument("--only-firefox", action="store_true")
    only_app_group.add_argument("--only-msoffice", action="store_true")

    parser.add_argument("pickle_manifest")
    parser.add_argument("output_html")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
