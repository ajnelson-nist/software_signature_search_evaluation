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

__version__ = "0.0.11"

import logging
import os
import pickle
import sqlite3
import collections
import operator

_logger = logging.getLogger(os.path.basename(__file__))

import SignatureSearcher

def app_name_and_version(lcursor, etid):
    lcursor.execute("SELECT * FROM etid_to_productname WHERE ETID = ?;", (etid,))
    row = lcursor.fetchone()
    if row is None:
        raise ValueError("ETID not in label database: %r." % etid)
    return (row["ProductName"], row["Version"])

def main():
    searcher = SignatureSearcher.SignatureSearcher()

    lconn = sqlite3.connect(args.labels_db)
    lconn.row_factory = sqlite3.Row
    lcursor = lconn.cursor()

    _logger.debug("Loading searcher pickle...")
    searcher.load(args.searcher_pickle)
    _logger.debug("Done loading searcher pickle.")

    _logger.debug("Loading query...")
    _logger.info("Query is being built only from terms in VSM.")
    source_path_to_term_list = collections.defaultdict(list)
    query_terms = []
    qconn = sqlite3.connect(args.query_db)
    qconn.row_factory = sqlite3.Row
    qcursor = qconn.cursor()

    qcursor.execute("SELECT term, tally FROM query;")
    row_count = 0
    for row in qcursor:
        row_count += 1
        for x in range(row["tally"]):
            query_terms.append(row["term"])
    _logger.debug("Done loading query.")
    _logger.debug("len(query_terms) = %d." % len(query_terms))
    _logger.debug("len(query_terms in VSM) = %d." % len([term for term in query_terms if term in searcher.vsm.df]))

    _logger.debug("Building source_path_to_term_list...")
    qcursor.execute("ATTACH DATABASE '%s' AS term;" % args.term_db)
    qcursor.execute("""\
SELECT
  p.cellpath,
  t.term
FROM
  term.paths AS p,
  term.terms AS t
WHERE
  t.source_path_id = path_id
;""")
    for row in qcursor:
        if searcher.vsm.df.get(row["term"]):
            source_path_to_term_list[row["cellpath"]].append(row["term"])
    qcursor.execute("DETACH DATABASE term;")
    _logger.debug("Done building source_path_to_term_list.")

    _logger.info("Loading pre-computed signature search query results...")
    results = None
    with open(args.query_results_pickle, "rb") as query_results_fh:
        unpickler = pickle.Unpickler(query_results_fh)
        results = unpickler.load()
    _logger.info("Done loading pre-computed signature search query results.")

    _logger.info("Inspecting %d results..." % len(results))
    _logger.debug("results = %r." % results)
    _logger.debug("searcher.doc_threshold = %r." % searcher.doc_threshold)
    hits = []
    misses = []
    for (score, doc_name) in results:
    #E.g. (0.010948376651342248, '15146-1/Close')
        if doc_name in searcher.doc_threshold:
            if score >= searcher.doc_threshold[doc_name]:
                hits.append((score, doc_name))
            else:
                misses.append((score, doc_name))
    _logger.info("Inspected results.")
    _logger.info("%d hits." % len(hits))
    _logger.info("%d misses." % len(misses))
    _logger.debug("hits = %r." % hits)

    gtdict = dict()
    if args.ground_truth_db:
        with sqlite3.connect(args.ground_truth_db) as gtconn:
            gtconn.row_factory = sqlite3.Row
            gtcursor = gtconn.cursor()
            gtcursor.execute("SELECT * FROM ground_truth;")
            for gtrow in gtcursor:
                gtdict[(gtrow["node_id"], gtrow["doc_name"])] = {
                  0: False,
                  1: True
                }.get(gtrow["present"])
    _logger.debug("gtdict = %r." % gtdict)

    with open(args.out_html, "w") as out_fh:
        if args.short_tables:
            tables_note = "Short tables requested; only the top 100 Registry cell names will be listed for each signature evidence set."
        else:
            tables_note = "Full tables requested; all Registry cell names will be listed for each signature evidence set."

        if args.ground_truth_db:
            ground_truth_info = """\
      <dt>Ground truth annotations</dt>
      <dd>Ground truth annotations were supplied to indicate which Searcher hits and misses are correct (&check;) and incorrect (&cross;).</dd>
"""
        else:
            ground_truth_info = ""

        #Document header
        out_fh.write("""\
<!DOCTYPE html>
<html>
  <head>
    <title>Signature Searcher results</title>
    <style type="text/css">
      #match_summary th {text-align:left;}
      #match_summary tbody th {font-style:italic;}
      thead th {text-decoration:underline;};
      .todo {font-color:red;}
    </style>
  </head>
  <body>
    <h1>Signature Searcher results</h1>
    <dl>
      <dt>Input signature searcher</dt>
      <dd><code>%s</code></dd>
      <dt>Input query</dt>
      <dd><code>%s</code></dd>
      <dt>Evidence table length</dt>
      <dd>%s</dd>
%s
    </dl>
""" % (args.searcher_pickle, args.query_db, tables_note, ground_truth_info))

        #Summary section
        out_fh.write("""\
    <section>
      <h2>Summary</h2>
      <p>These applications' signatures were considered to match or fail to match against the input Registry, indicating wheter the software was present and/or run.</p>
      <table id="match_summary">
        <thead>
          <tr>
            <th>Application name</th>
            <th>Version</th>
            <th>Installed</th>
            <th>Run</th>
          </tr>
        </thead>
        <tfoot></tfoot>
        <tbody>
""")

        #Group hits by ETIDs
        #Key:  ETID (singleton or /-delimited pair.)
        #Value:  Dictionary.
        #    Key:  "Install" or "Run".
        #    Value:  "Yes" or "No"
        hits_by_etids = collections.defaultdict(dict)
        ground_truth_matches = collections.defaultdict(dict) #Same structure, but the last value is True or False.
        for (is_hit, _list) in [("Yes", hits), ("No", misses)]:
            for (score, doc_name) in _list:
                doc_name_parts = doc_name.split("/")
                etids = "/".join(doc_name_parts[:-1])
                #Install/run
                if doc_name_parts[-1] == "Install":
                    ir = "Install"
                else:
                    ir = "Run"
                hits_by_etids[etids][ir] = is_hit

                if args.ground_truth_db:
                    should_be_hit = gtdict.get((args.ground_truth_node_id, doc_name)) #Using .get() because this may request a signature that never existed, like for an application that only installs and has no definable "run" signature.
                    if should_be_hit is None:
                        ground_truth_match = None
                    elif should_be_hit == True and is_hit == "Yes":
                        ground_truth_match = True
                    elif should_be_hit == False and is_hit == "No":
                        ground_truth_match = True
                    else:
                        ground_truth_match = False
                    ground_truth_matches[etids][ir] = ground_truth_match
        _logger.debug("hits_by_etids = %r." % hits_by_etids)
        _logger.debug("ground_truth_matches = %r." % ground_truth_matches)

        for etids in sorted(hits_by_etids.keys()):
            etids_list = etids.split("/")
            appetid = etids_list[-1]
            osetid = None if len(etids_list) == 1 else etids_list[0]

            formatd = dict()
            formatd["etids"] = etids

            (app_name, app_version) = app_name_and_version(lcursor, appetid)
            formatd["application_name"] = app_name
            formatd["application_version"] = app_version

            out_fh.write("""\
          <tr>
            <th>%(application_name)s</th>
            <td>%(application_version)s</td>
""" % formatd)

            #Install column
            formatd["is_hit"] = hits_by_etids[etids].get("Install")
            ground_truth_match = ground_truth_matches[etids].get("Install")
            if ground_truth_match == True:
                formatd["ground_truth_anno"] = " (&check;)"
            elif ground_truth_match == False:
                formatd["ground_truth_anno"] = " (&cross;)"
            else:
                formatd["ground_truth_anno"] = ""
            if formatd["is_hit"] is None:
                out_fh.write("""\
            <td>%(ground_truth_anno)sN/A</td>
""" % formatd)
            else:
                out_fh.write("""\
            <td><a href="#%(etids)s/Install">%(is_hit)s</a>%(ground_truth_anno)s</td>
""" % formatd)

            #Run column
            formatd["is_hit"] = hits_by_etids[etids].get("Run")
            ground_truth_match = ground_truth_matches[etids].get("Run")
            if ground_truth_match == True:
                formatd["ground_truth_anno"] = " (&check;)"
            elif ground_truth_match == False:
                formatd["ground_truth_anno"] = " (&cross;)"
            else:
                formatd["ground_truth_anno"] = ""
            if formatd["is_hit"] is None:
                out_fh.write("""\
            <td>%(ground_truth_anno)sN/A</td>
""" % formatd)
            else:
                out_fh.write("""\
            <td><a href="#%(etids)s/Run">%(is_hit)s</a>%(ground_truth_anno)s</td>
""" % formatd)

            out_fh.write("""\
          </tr>
""")
        out_fh.write("""\
        </tbody>
      </table>
    <p>There are sections for listing evidence for signature matches [<a href="#hits">1</a>], or insufficiency for signature matches [<a href="#misses">2</a>].</p>
    </section>
""")

        for _list in [hits, misses]:
            if _list == hits:
                section_header = """\
    <section>
      <h2><a name="hits" />Evidence for signature matches</h2>
      <p>Each signature match has supporting evidence presented here.</p>
"""
            else:
                section_header = """\
    <section>
      <h2><a name="misses" />Similarity scores for signature non-matches</h2>
      <p>Each signature with insufficient evidence in the query to match is presented here.</p>
"""

            #Evidence section
            out_fh.write(section_header)
            for (score, doc_name) in _list:
                doc_name_parts = doc_name.split("/")
                appetid = doc_name_parts[-2]
                slicetype = doc_name_parts[-1]
                (app_name, app_version) = app_name_and_version(lcursor, appetid)

                formatd = dict()
                formatd["doc_name"] = doc_name
                formatd["app_name"] = app_name
                formatd["app_version"] = app_version
                formatd["slicetype"] = slicetype
                formatd["threshold"] = searcher.doc_threshold[doc_name]
                formatd["score"] = score

                out_fh.write("""\
      <section>
        <h3><a name="%(doc_name)s">%(app_name)s; %(app_version)s; %(slicetype)s</a></h3>
""" % formatd)

#                out_fh.write("""\
#            <p>This signature was sourced primarily from these Diskprint change sets:</p>
#            <ul>
#              <li>234-1-234-1-100:234-1-15151-1-10</li>
#              <li>234-1-15151-1-10:234-1-15151-1-30</li>
#            </ul>
#""")

                reporting_tuples = []
                _logger.debug("Assembling weight tuples for doc_name %r..." % doc_name)
                for source_path in source_path_to_term_list:
                    source_path_weight = 0
                    for term in set(source_path_to_term_list[source_path]):
                        source_path_weight += searcher.vsm.tfidf[doc_name].get(term, 0)
                    if source_path_weight == 0:
                        continue

                    signature_aggregate_weight = 0
                    for term in set(source_path_to_term_list[source_path]):
                        signature_aggregate_weight += searcher.vsm.tfidf[doc_name].get(term, 0)

                    reporting_tuples.append((signature_aggregate_weight, source_path))
                _logger.debug("Done assembling weight tuples for doc_name %r." % doc_name)
                _logger.debug("%d weight tuples after filtering 0-tfidf weights." % len(reporting_tuples))
                formatd["term_tally"] = len(reporting_tuples)

                out_fh.write("""\
        <p>The similarity threshold for this application is %(threshold)r, and the input query scored %(score)r.  The signature and query had %(term_tally)d terms in common, with the following weights (listed in descending weight order):</p>
        <table>
          <thead>
            <tr>
              <th>Signature weight</th>
              <th>Term</th>
            </tr>
          </thead>
          <tfoot></tfoot>
          <tbody>
""" % formatd)

                #Sort by path and then by weights.
                reporting_tuples_sbt = sorted(reporting_tuples, key=operator.itemgetter(1))
                for (reporting_tuple_no, reporting_tuple) in enumerate(sorted(reporting_tuples_sbt, key=operator.itemgetter(0), reverse=True)):
                    if args.short_tables and reporting_tuple_no > 100:
                        break
                    out_fh.write("""\
            <tr>
              <td>%r</td>
              <td><code>%s</code></li>
            </tr>
""" % reporting_tuple)
                out_fh.write("""\
          </tbody>
        </table>
      </section>
""")
            out_fh.write("""\
    </section>
""")

        #Training section
#        out_fh.write("""\
#    <section>
#      <h2>Signature Searcher Training Data</h2>
#      <p class="TODO">(Coming soon - this section is currently a sample.)</p>
#      <p>This Signature Searcher was trained on the data in the following table.</p>
#      <table id="training_summary">
#        <thead>
#          <tr>
#            <th>ETID</th>
#            <th></th>
#            <th></th>
#            <th></th>
#            <th></th>
#          </tr>
#        </thead>
#      </table>
#    </section>
#""")

        out_fh.write("""\
  </body>
</html>
""")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--short-tables", action="store_true")
    parser.add_argument("--ground-truth-db")
    parser.add_argument("--ground-truth-node-id")
    parser.add_argument("labels_db")
    parser.add_argument("searcher_pickle")
    parser.add_argument("term_db")
    parser.add_argument("query_db")
    parser.add_argument("query_results_pickle")
    parser.add_argument("out_html")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
