#!/usr/bin/env/python3

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

__version__ = "0.11.1"

import logging
import os
import sqlite3
import pickle
import collections
import copy

_logger = logging.getLogger(os.path.basename(__file__))

import n_grammer
import normalizer
import stoplisted_query
import TFIDFEngine

def stop_list_structs(stop_list_db, stop_list_n_gram_strategy):
    #Only populate one of these data structures, depending on the stop list strategy.
    path_stop_list = set()
    term_stop_list = set()
    term_threshold = dict() #Key: term (string); Value: tally (intger)
    slconn = sqlite3.connect(stop_list_db)
    slconn.row_factory = sqlite3.Row
    slcursor = slconn.cursor()
    if stop_list_n_gram_strategy == "raw_filter":
        slcursor.execute("SELECT cellpath FROM path_stop_list;")
        for row in slcursor:
            path_stop_list.add(row["cellpath"])
    elif stop_list_n_gram_strategy == "n_gram_blacklist":
        slcursor.execute("SELECT term FROM term_stop_list;")
        for row in slcursor:
            term_stop_list.add(row["term"])
    elif stop_list_n_gram_strategy == "n_gram_threshold":
        slcursor.execute("SELECT term, tally FROM term_threshold;")
        for row in slcursor:
            term_threshold[row["term"]] = row["tally"]
    else:
        raise NotImplementedError("Stop list n-gram strategy logic not implemented: %r." % stop_list_n_gram_strategy)
    slcursor.close()
    slconn.close()
    return (path_stop_list, term_stop_list, term_threshold)

def main():
    global args

    if not args.cell_parent_pickle is None:
        _logger.debug("Loading cell parent map...")
        with open(args.cell_parent_pickle, "rb") as cp_fh:
            unpickler = pickle.Unpickler(cp_fh)
            n_grammer.parent_map = unpickler.load()
        _logger.debug("Done loading cell parent map.")

    meta_conn = sqlite3.connect(":memory:")
    meta_conn.row_factory = sqlite3.Row
    meta_cursor = meta_conn.cursor()

    meta_cursor.execute("ATTACH DATABASE '%s' AS namedsequence;" % args.namedsequence_db)
    meta_cursor.execute("ATTACH DATABASE '%s' AS slice;" % args.slice_db)

    #Try to reduce seek times
    #cursor.execute("PRAGMA cache_size = 2097152;") #2 GiB

    engine = TFIDFEngine.BasicTFIDFEngine()

    #Load stop list (note that path normalizing has already occurred before load time)
    (path_stop_list, term_stop_list, term_threshold) = stop_list_structs(args.stop_list_db, args.stop_list_n_gram_strategy)

    #Key: Document name.
    #Value: List of term lists (lists because terms can repeat in a single change set).
    sequence_term_lists = collections.defaultdict(list)

    #Assemble the lists of documents that should exist.
    #This will require the namedsequence and slice tables (slice table for slice types).
    #(NOTE: The query excludes beginning-of-sequence nodes, because their predecessors are NULL and thus won't match in a join on equality.  This is intentional behavior.)
    meta_cursor.execute("""\
SELECT
  ns.*,
  s.slicetype
FROM
  namedsequence.namedsequence AS ns,
  slice.slice AS s
WHERE
  ns.osetid = s.osetid AND
  ns.appetid = s.appetid AND
  ns.sliceid = s.sliceid AND
  ns.sequencelabel LIKE '""" + args.prefix + """-%'
;""")
    for meta_row in meta_cursor:
        node_id = "%(osetid)s-%(appetid)s-%(sliceid)d" % meta_row
        predecessor_node_id = "%(predecessor_osetid)s-%(predecessor_appetid)s-%(predecessor_sliceid)d" % meta_row

        if args.by_app:
            doc_name = "%(appetid)s/%(slicetype)s" % meta_row
        elif args.by_osapp:
            doc_name = "%(osetid)s/%(appetid)s/%(slicetype)s" % meta_row
        else:
            raise NotImplementedError("Only --by-app and --by-osapp are implemented.")

        new_cell_db_path = os.path.join(args.dwf_results_root, "by_edge", predecessor_node_id, node_id, "make_registry_diff_db.sh", "registry_new_cellnames.db")
        _logger.debug("Ingesting new-cell database %r." % new_cell_db_path)
        with sqlite3.connect(new_cell_db_path) as new_cell_db_conn:
            new_cell_db_conn.row_factory = sqlite3.Row
            new_cell_db_cursor = new_cell_db_conn.cursor()
            new_cell_db_cursor.execute("""\
SELECT
  filename,
  cellname
FROM
  hive_analysis AS h,
  cell_analysis AS c
WHERE
  h.hive_id = c.hive_id
;""")
            rows_procced = 0
            num_terms_added = 0
            current_term_list = []
            for row in new_cell_db_cursor:
                if args.normalize:
                    cellpath = normalizer.normalize_path(row["filename"], row["cellname"])
                else:
                    cellpath = row["cellname"]
                #Filter according to n-gram and stop list interaction.
                if args.stop_list_n_gram_strategy == "raw_filter":
                    if cellpath in path_stop_list:
                        continue

                derived_terms = []
                if args.n_gram_length is None:
                    derived_terms.append(cellpath)
                else:
                    for n_gram in n_grammer.n_grams(cellpath, int(args.n_gram_length), args.last_n):
                        derived_terms.append(n_gram)

                for derived_term in derived_terms:
                    if args.stop_list_n_gram_strategy == "n_gram_blacklist":
                        if derived_term in term_stop_list:
                            continue
                    current_term_list.append(derived_term)
                    num_terms_added += 1
                rows_procced += 1
            sequence_term_lists[doc_name].append(current_term_list)
            _logger.debug("    Added %d terms to sequence term list, derived from %d cell paths." % (num_terms_added, rows_procced))

    meta_cursor.execute("DETACH DATABASE namedsequence;")
    meta_cursor.execute("DETACH DATABASE slice;")

    #This seems to be the cleanest way to write a fold (e.g. reduce) call for many-set intersection.
    doc_names = sorted(sequence_term_lists.keys())

    #Assemble documents from change sets
    num_doc_names = len(doc_names)
    docs_to_ingest = [] #List of tuples: (Doc length, doc name, doc term list)
    for (doc_name_no, doc_name) in enumerate(doc_names):
        #Build glomming, union and/or intersection of documents.
        #(NOTE type looseness:  doc_summation is a list, the others are sets.)
        doc_union = set([])
        doc_intersection = None
        doc_summation = []
        previous_doc_len = None # Running state record for current document, not a reference to the prior document

        _logger.debug("Combining %d sequence term lists for document %r." % (len(sequence_term_lists[doc_name]), doc_name))
        for term_list in sequence_term_lists[doc_name]:
            if args.summation or args.sumint:
                doc_summation.extend(term_list)

            if args.union or args.inconsistent:
                tmpset = set(term_list)
                doc_union = doc_union.union(tmpset)

            if args.intersection or args.inconsistent or args.sumint:
                tmpset = set(term_list)
                if doc_intersection is None:
                    doc_intersection = tmpset
                else:
                    doc_intersection = doc_intersection.intersection(tmpset)
                if not previous_doc_len is None:
                    _logger.debug("    Remaining terms after intersection, doc_name %r: %d, down from %r." % (doc_name, len(doc_intersection), previous_doc_len))
                previous_doc_len = len(doc_intersection)

        #Quick hack: Type safety in case of empty term lists.
        if doc_intersection is None: doc_intersection = set([])

        #Pick document according to arguments' request.
        #The type of doc is list.
        if args.summation:
            doc = doc_summation
        elif args.union:
            doc = [term for term in doc_union]
        elif args.intersection:
            doc = [term for term in doc_intersection]
        elif args.inconsistent:
            doc = [term for term in (doc_union - doc_intersection)]
        elif args.sumint:
            doc = [term for term in doc_summation if term in doc_intersection]
        else:
            raise ValueError("Combinator parameter missing combination logic.")

        #Filter out stoplist terms according to strategy
        if args.stop_list_n_gram_strategy == "n_gram_threshold":
            doc_vector = collections.defaultdict(int)
            for term in doc:
                doc_vector[term] += 1
            for term in term_threshold.keys():
                if doc_vector.get(term) is None:
                    continue
                doc_vector[term] -= term_threshold[term]
            #Reset doc list
            doc = []
            for term in doc_vector:
                if doc_vector[term] > 0:
                    for x in range(doc_vector[term]):
                        doc.append(term)

        _logger.debug("Combined document %r (%d terms)..." % (doc_name, len(doc)))

        docs_to_ingest.append((len(doc), doc_name, doc))

    #Ingest documents into TFIDF object
    #(It is substantially slower to ingest the bigger documents first.)
    doc_ingest_count = 0
    for (doc_no, (doc_len, doc_name, doc)) in enumerate(sorted(docs_to_ingest)):
        _logger.debug("Ingesting document %r to TFIDF data object (%d terms)..." % (doc_name, len(doc)))
        engine.ingest_document(doc_name, doc)
        doc_ingest_count += 1
        _logger.debug("Done ingesting document %d of %d." % (doc_no+1, num_doc_names))

    _logger.debug("Ingested %d documents." % doc_ingest_count)
    #This is not an error, it is just exceptional but tolerable behavior.
    #if doc_ingest_count == 0:
    #    raise Exception("This model failed to ingest any documents.")

    engine.save(args.pickle)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Turn on debug-level logging.", action="store_true")
    parser.add_argument("--last-n", action="store_true", help="Only use last n terms of query (n set by --n-gram-length).")
    parser.add_argument("--n-gram-length", type=int)
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--prefix", help="Sequence label prefix; supply a string to filter to include only sequences with this prefix.", default="")
    parser.add_argument("--stop-list-n-gram-strategy", choices=stoplisted_query.stop_list_n_gram_strategy_whitelist, required=True)
    parser.add_argument("--cell-parent-pickle", help="Dictionary derived from cell_parent_db.py and dump_parent_map.py.  Only needed if --n-gram-length is used.")
    parser.add_argument("stop_list_db", help="SQLite database containing stoplist cell paths.")
    parser.add_argument("namedsequence_db")
    parser.add_argument("slice_db")
    parser.add_argument("dwf_results_root")
    parser.add_argument("pickle", help="Persist TFIDF object as a Python-Pickle'd file at this path.")

    #Require union or intersection
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--summation", action="store_true", help="Build model based on counting terms of all sets.")
    input_group.add_argument("--union", action="store_true", help="Build model based on unions of term sets.")
    input_group.add_argument("--intersection", action="store_true", help="Build model based on intersections of term sets.")
    input_group.add_argument("--inconsistent", action="store_true", help="Build model based on difference of union and intersection of term sets.  Note that this is not theoretically satisfying as a model by itself, but serves to improve the other models indirectly.")
    input_group.add_argument("--sumint", action="store_true", help="Build model based on summation-intersection of term sets (intersection multiplied by counts of intersecting terms).")

    docsby_group = parser.add_mutually_exclusive_group(required=True)
    docsby_group.add_argument("--by-app", action="store_true", help="Group document names by AppETID and SliceType.")
    docsby_group.add_argument("--by-osapp", action="store_true", help="Group document names by OSETID, AppETID, and SliceType.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
