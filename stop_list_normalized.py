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

__version__ = "2.2.7"

import logging
import os
import sqlite3
import collections
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer
import n_grammer

def main():
    global args

    inconn = sqlite3.connect(args.namedsequences_db)
    inconn.row_factory = sqlite3.Row
    incursor = inconn.cursor()

    outconn = sqlite3.connect(args.output_db)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    outcursor.execute("CREATE TEMPORARY TABLE temp_path_stop_list (cellpath TEXT UNIQUE);")

    outcursor.execute("CREATE TABLE path_stop_list (cellpath TEXT UNIQUE);")
    outcursor.execute("CREATE TABLE term_stop_list (term TEXT UNIQUE);")
    outcursor.execute("CREATE TABLE term_threshold (term TEXT UNIQUE, tally INTEGER);")

    # This script could probably be cleaner by using the results of reg_db_to_term_list.py.
    # (The Tao of TODO: Not all need be done.)

    incursor.execute("""\
SELECT
  *
FROM
  namedsequence
WHERE
  sequencelabel LIKE '""" + ("baseline" if args.baseline else "preinstalled") + """-%'
ORDER BY
  osetid,
  appetid,
  sliceid
;""")
    _logger.debug("Loading table temp_path_stop_list...")
    node_ids = []
    for (seqrow_no, seqrow) in enumerate(incursor):
        node_id = "%(osetid)s-%(appetid)s-%(sliceid)d" % seqrow
        node_ids.append(node_id)
    #Check that the databases exist before running expensive inserts only to fail on not finding one later.
    for node_id in node_ids:
        node_db_path = os.path.join(args.dwf_results_root, "by_node", node_id, "format_registry_single_state.sh", "registry_single_state.db")
        if not os.path.exists(node_db_path):
            raise FileNotFoundError("Expecting to read non-existent file: %r." % node_db_path)
    for node_id in node_ids:
        node_db_path = os.path.join(args.dwf_results_root, "by_node", node_id, "format_registry_single_state.sh", "registry_single_state.db")
        _logger.debug("Ingesting Registry cell database %r." % node_db_path)
        with sqlite3.connect(node_db_path) as nodeconn:
            nodeconn.row_factory = sqlite3.Row
            nodecursor = nodeconn.cursor()
            def _generate_cellpaths():
                nodecursor.execute("""\
SELECT
  filename,
  cellname
FROM
  hive_analysis AS h,
  cell_analysis AS c
WHERE
  h.hive_id = c.hive_id
;""")
                for noderow in nodecursor:
                    if args.normalize:
                        cellpath = normalizer.normalize_path(noderow["filename"], noderow["cellname"])
                    else:
                        cellpath = noderow["cellname"]
                    yield (cellpath,)
            outcursor.executemany("INSERT OR IGNORE INTO temp_path_stop_list(cellpath) VALUES (?);", _generate_cellpaths())
    _logger.debug("Done loading table temp_path_stop_list.")

    #Build final path stop list table before derived-terms tables.
    _logger.debug("Sorting results out of temporary table (whole paths).")
    outcursor.execute("""\
INSERT INTO path_stop_list(cellpath)
  SELECT DISTINCT
    cellpath
  FROM
    temp_path_stop_list
  ORDER BY
    cellpath
;""")
    _logger.debug("Done sorting (whole paths).")

    rcursor = outconn.cursor()
    wcursor = outconn.cursor()

    if args.n_gram_length is None:
        _logger.debug("Sorting results out of temporary table (unigrams).")
        outcursor.execute("""\
INSERT INTO term_stop_list(term)
  SELECT DISTINCT 
    cellpath AS term
  FROM
    path_stop_list
  ORDER BY
    term
;""")
        _logger.debug("Done sorting (unigrams).")
        _logger.debug("Counting unigrams for thresholds.")
        outcursor.execute("""\
INSERT INTO term_threshold(term, tally)
  SELECT
    cellpath AS term,
    COUNT(*) AS tally
  FROM
    temp_path_stop_list
  GROUP BY
    cellpath
  ORDER BY
    term
;""")
        _logger.debug("Done counting unigrams for thresholds.")
    else:
        _logger.debug("Loading cell parent pickle.")
        with open(args.cell_parent_pickle, "rb") as cp_fh:
            unpickler = pickle.Unpickler(cp_fh)
            n_grammer.parent_map = unpickler.load()
        _logger.debug("Done loading cell parent pickle.")

        derived_terms_tallies = collections.defaultdict(int)

        _logger.debug("Counting n-gram occurences.")
        rcursor.execute("SELECT cellpath FROM path_stop_list;")
        for row in rcursor:
            #Create all n-grams from term and parents.
            for n_gram in n_grammer.n_grams(row["cellpath"], int(args.n_gram_length), args.last_n):
                derived_terms_tallies[n_gram] += 1
        _logger.debug("Done counting n-gram occurences.")

        #Ingest into stop list and threshold table after building counts.
        _logger.debug("Loading n-grams for stop list.")
        def _generate_terms():
            #(This seems easier to read than a list comprehension.)
            for key in sorted(derived_terms_tallies.keys()):
                yield (key,)
        wcursor.executemany("INSERT INTO term_stop_list (term) VALUES (?);", _generate_terms())
        _logger.debug("Loading n-grams for list thresholds.")
        def _generate_thresholds():
            for key in sorted(derived_terms_tallies.keys()):
                yield (key, derived_terms_tallies[key])
        wcursor.executemany("INSERT INTO term_threshold (term, tally) VALUES (?,?);", _generate_thresholds())
        _logger.debug("Done loading n-grams for stop list and thresholds.")

    _logger.debug("Creating indices.")
    wcursor.execute("CREATE INDEX idx_path_stop_list ON path_stop_list (cellpath);")
    wcursor.execute("CREATE INDEX idx_term_stop_list ON term_stop_list (term);")
    wcursor.execute("CREATE INDEX idx_term_threshold ON term_threshold (term);")
    _logger.debug("Done.")

    outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--normalize", action="store_true")

    parser.add_argument("--last-n", action="store_true", help="Only use last n components of path (n set by --n-gram-length).")
    parser.add_argument("--n-gram-length", type=int)
    parser.add_argument("--cell-parent-pickle", help="Gzip'd dictionary derived from cell_parent_db.py and dump_parent_map.py.")

    parser.add_argument("namedsequences_db")
    parser.add_argument("dwf_results_root")
    parser.add_argument("output_db")

    #Require baseline or preinstalleds
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--baseline", action="store_true", help="Build stop lists from all baseline prints' cells.")
    input_group.add_argument("--preinstalled", action="store_true", help="Build stop lists from all preinstalled apps' prints' cells.")

    args = parser.parse_args()

    if not args.n_gram_length is None:
        if args.cell_parent_pickle is None:
            raise ValueError("Must supply cell parent pickle, because n-gram lenth was supplied.")

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
