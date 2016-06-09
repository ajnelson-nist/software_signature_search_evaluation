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

__version__ = "0.11.1"

import logging
import os
import sqlite3
import collections
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import vsm_set_theory_ops

stop_list_n_gram_strategy_whitelist = ["raw_filter", "n_gram_blacklist", "n_gram_threshold"]

def main():
    conn = sqlite3.connect(args.out_db)
    #conn.isolation_level = "EXCLUSIVE" #Don't do this.  It locks attached databases too.
    conn.row_factory = sqlite3.Row
    rcursor = conn.cursor()
    wcursor = conn.cursor()

    if args.stop_list_n_gram_strategy == "n_gram_threshold":
        _logger.debug("Loading stop list structures.")
        (path_stop_list, term_stop_list, term_threshold) = vsm_set_theory_ops.stop_list_structs(args.stoplist_db, args.stop_list_n_gram_strategy)
    else:
        #Most of the stop list work will be handled in SQL, to ease memory pressure.
        (path_stop_list, term_stop_list, term_threshold) = ( set(), set(), dict() )
        _logger.debug("Attaching stop list database %r." % args.stoplist_db)
        wcursor.execute("ATTACH DATABASE '%s' AS stoplist;" % args.stoplist_db)

    _logger.debug("Attaching Registry term list database %r." % args.reg_terms_db)
    wcursor.execute("ATTACH DATABASE '%s' AS regterms;" % args.reg_terms_db)

    ##Try to reduce seek times
    #wcursor.execute("PRAGMA cache_size = 2097152;") #2 GiB (page sizes default 1KiB)
    #wcursor.execute("PRAGMA rss.cache_size = 1048576;") #1 GiB

    wcursor.execute("CREATE TABLE query (term TEXT, tally INTEGER);")
    conn.commit()

    #The interactions added in this script are the stop list n-gram strategy, and the stop list.
    query_term_tally = collections.defaultdict(int)
    _logger.debug("Counting term occurrences...")
    if args.stop_list_n_gram_strategy == "raw_filter":
        rcursor.execute("""\
SELECT
  term,
  COUNT(*) AS tally
FROM
  regterms.terms AS i_t,
  regterms.paths AS i_p
WHERE
  i_t.source_path_id = i_p.path_id AND
  cellpath NOT IN (
    SELECT
      cellpath
    FROM
      stoplist.path_stop_list
  )
GROUP BY
  term
;""")
    elif args.stop_list_n_gram_strategy == "n_gram_blacklist":
        rcursor.execute("""\
SELECT
  term,
  COUNT(*) AS tally
FROM
  regterms.terms
WHERE
  term NOT IN (
    SELECT
      term
    FROM
      stoplist.term_stop_list
  )
GROUP BY
  term
;""")
    elif args.stop_list_n_gram_strategy == "n_gram_threshold":
        rcursor.execute("SELECT term, COUNT(*) AS tally FROM regterms.terms GROUP BY term;")
    _logger.debug("Done grouping term occurrences.  Filtering into query...")
    def _generate_query():
        for row in rcursor:
            query_term_tally[row["term"]] += row["tally"]
        if args.stop_list_n_gram_strategy == "n_gram_threshold":
            for term in term_threshold:
                if not query_term_tally.get(term) is None:
                    query_term_tally[term] -= term_threshold[term]
        for term in sorted(query_term_tally.keys()):
            if query_term_tally[term] <= 0:
                continue

            yield (term, query_term_tally[term])
    wcursor.executemany("INSERT INTO query (term, tally) VALUES(?,?);", _generate_query())
    _logger.debug("Done building query.")

    #The query is unlikely to need an index.

    _logger.debug("Committing.")
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")

    #Require n-gram interaction strategy
    parser.add_argument("--stop-list-n-gram-strategy", required=True, choices=stop_list_n_gram_strategy_whitelist)

    parser.add_argument("stoplist_db")
    parser.add_argument("reg_terms_db")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
