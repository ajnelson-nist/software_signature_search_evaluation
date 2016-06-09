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

"""Makefile generator, to create searcher_scores.db."""

__version__ = "0.0.59"

import sqlite3
import os
import logging
import collections

_logger = logging.getLogger(os.path.basename(__file__))

import m57_meta

_datasets = ["training", "evaluation", "m57"]
_sequences = ["installclose", "repeated", "experiment1"]
_paths = ["normalized", "raw"]
_docs_bys = ["app", "osapp"]
_combinators = ["inconsistent", "sumint", "intersection", "summation"]
_stop_lists = ["none", "baseline", "bp", "bpi"] #"inconsistent" does not appear as a stop list in this list, because no models should be built on it.
_versions = ["distinct", "grouped"]
_n_grams = ["1", "2", "3", "all", "last1", "last2", "last3"]
_score_selectors = ["avg", "max", "min"]
_stop_list_n_gram_strategies = ["raw_filter", "n_gram_blacklist", "n_gram_threshold"]

def main():
    conn = sqlite3.connect(args.sequences_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #Key: Target file.
    #Value: Entire rule text.
    rules_misc = dict()

    #Key: Target file, a text file that contains a list of files, to be fed into another script.
    #Value: List of dependencies.
    rules_dependency_listing = collections.defaultdict(list)

    #This target is the objective of this entire script.  Below this line fills in the execution path starting from the downloaded Registry data.
    rules_misc["searcher_scores.db"] = """\
searcher_scores.db: \\
  doc_statistics.db \\
  rank_searchers.db \\
  searcher_scores.sql
	rm -f _$@
	$(GTIME) --verbose --output=$@.time.log sqlite3 _$@ < searcher_scores.sql 
	mv _$@ $@
"""
    rules_misc["doc_statistics.db"] = """\
doc_statistics.db: \\
  doc_statistics_db.py \\
  rank_searchers_db.py \\
  signature_statistics_manifest.txt
	rm -f _$@
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) doc_statistics_db.py $(DEBUG_FLAG) signature_statistics_manifest.txt _$@
	mv _$@ $@
"""

    rules_misc["rank_searchers.db"] = """\
rank_searchers.db: \\
  rank_searchers_db.py \\
  signature_searcher_measurement_manifest.txt
	rm -f _$@
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) rank_searchers_db.py $(DEBUG_FLAG) signature_searcher_measurement_manifest.txt _$@
	mv _$@ $@
"""

    #Key: Dataset.
    #Value: Set of node (as in lineage node) IDs of the dataset.
    node_ids = collections.defaultdict(set)

    #Assemble list of nodes used for diskprint training data.
    #This set is filtered in the next code block's OS walk for nodes that had successful RegXML Extractor runs.
    for docs_by in _docs_bys:
        with sqlite3.connect("ground_truth/data_training/docs_by_%s/versions_distinct/ground_truth_positive.db" % docs_by) as gtconn:
            gtconn.row_factory = sqlite3.Row
            gtcursor = gtconn.cursor()
            gtcursor.execute("SELECT DISTINCT node_id FROM ground_truth_positive;")
            for row in gtcursor:
                node_ids["training"].add(row["node_id"])
    _logger.debug("Training node IDs from ground truth database: %r." % node_ids["training"])

    #Assemble list of nodes, all diskprint data.
    by_node_root = os.path.join(args.dewf_results_diskprints, "by_node")
    for (dirpath, dirnames, filenames) in os.walk(by_node_root):
        #Only inspect top level.
        if dirpath != by_node_root:
            continue
        for node_id in dirnames:
            node_ids["diskprints"].add(node_id)

    #Assemble list of nodes, all M57 data for analysis.
    for machine_tag in m57_meta.MACHINE_TAG_SEQUENCES:
        for node_id in m57_meta.MACHINE_TAG_SEQUENCES[machine_tag]:
            #TODO Terry wasn't reported in Roussev & Quates.  Some day there should be an application dive through Terry's systems.
            if "terry" in node_id:
                continue
            node_ids["m57"].add(node_id)

    #Assemble list of nodes, all evaluation data.
    with open(args.experiment1_node_list, "r") as nl_fh:
        for line in nl_fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            node_ids["evaluation"].add(cleaned_line)
    for dataset in sorted(node_ids.keys()):
        _logger.debug("%d Node IDs for %s." % (len(node_ids[dataset]), dataset))

    #Stash path of each node's Registry database.
    #Key: Dataset.
    #Value: Dictionary
    #  Key: Node ID.
    #  Value: Path to downloaded Registry cell name database.
    node_registry_db = collections.defaultdict(dict)
    for (dataset, dewf_results_root) in [
      ("diskprints", args.dewf_results_diskprints),
      ("evaluation", args.dewf_results_evaluation),
      ("m57", args.dewf_results_m57),
      ("training", args.dewf_results_diskprints)
    ]:
        for node_id in sorted(node_ids[dataset]):
            db_relpath = os.path.join(dewf_results_root, "by_node", node_id, "format_registry_single_state.sh", "registry_single_state.db")
            #Vet DB existence.
            if not os.path.exists(db_relpath):
                raise ValueError("No Registry cell set database found for dataset %s, node %r.  Expecting this path: %r." % (dataset, node_id, db_relpath))
            node_registry_db[dataset][node_id] = db_relpath
    for dataset in sorted(node_registry_db.keys()):
        _logger.debug("%d Registry databases for %s." % (len(node_registry_db[dataset]), dataset))

    #Make parent-path database rules (training data will use soft-links)
    #Because the overwhelming majority of the experiment's computation time is constructing queries, precomputing n-gram sets saves a great amount of time.
    for dataset in sorted(node_registry_db.keys()):
        for path in _paths:
            metadict = dict()
            metadict["dataset"] = dataset
            metadict["path"] = path

            #This file's rule is rollup-list-populated at the end of the for-each-node_id loop.
            metadict["cell_parent_db_manifest_txt"] = "cell_parent/data_%(dataset)s/paths_%(path)s/cell_parent_db_manifest.txt" % metadict

            metadict["cell_parent_db"] = "cell_parent/data_%(dataset)s/paths_%(path)s/cell_parent.db" % metadict
            rules_misc[metadict["cell_parent_db"]] = """\
%(cell_parent_db)s: \\
  %(cell_parent_db_manifest_txt)s \\
  cell_parent_db.py \\
  cell_parent_db_rollup.py
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) cell_parent_db_rollup.py $(DEBUG_FLAG) %(cell_parent_db_manifest_txt)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

            #Roll up cell parents from the node_id loop after the n-gram loop.
            metadict["cell_parent_pickle"] = "cell_parent/data_%(dataset)s/paths_%(path)s/cell_parent.pickle" % metadict
            rules_misc[metadict["cell_parent_pickle"]] = """\
%(cell_parent_pickle)s: \\
  %(cell_parent_db)s \\
  dump_parent_map.py
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) dump_parent_map.py $(DEBUG_FLAG) %(cell_parent_db)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

            #Precompute n-grams.
            for n_grams in _n_grams:
                metadict["n_grams"] = n_grams
                if n_grams == "all":
                    metadict["n_grams_flag"] = ""
                elif n_grams.startswith("last"):
                    metadict["n_grams_flag"] = "--last-n --n-gram-length=%s" % n_grams[-1]
                else:
                    metadict["n_grams_flag"] = "--n-gram-length=%s" % n_grams
                metadict["n_gram_derivation_pickle"] = "n_gram_derivation/data_%(dataset)s/paths_%(path)s/n_grams_%(n_grams)s/n_gram_derivation.pickle" % metadict
                rules_misc[metadict["n_gram_derivation_pickle"]] = """\
%(n_gram_derivation_pickle)s: \\
  %(cell_parent_pickle)s \\
  n_gram_derivation_pickle.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) n_gram_derivation_pickle.py $(DEBUG_FLAG) %(n_grams_flag)s %(cell_parent_pickle)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

            #Create cell parent rules for each node
            for node_id in sorted(node_registry_db[dataset].keys()):
                metadict["node_id"] = node_id
                metadict["normalize_flag"] = "--normalize" if path=="normalized" else ""
                metadict["registry_db"] = node_registry_db[dataset][node_id]
                metadict["cell_parent_node_db"] = "cell_parent/data_%(dataset)s/paths_%(path)s/%(node_id)s.db" % metadict
                metadict["cell_parent_node_pickle"] = "cell_parent/data_%(dataset)s/paths_%(path)s/%(node_id)s.pickle" % metadict

                #The training dbs can be soft-linked.
                if dataset == "training":
                    metadict["diskprint_cell_parent_node_db"] = "cell_parent/data_diskprints/paths_%(path)s/%(node_id)s.db" % metadict
                    metadict["diskprint_cell_parent_node_abspath"] = os.path.join(os.path.realpath("."), metadict["diskprint_cell_parent_node_db"])
                    rules_misc[metadict["cell_parent_node_db"]] = """\
%(cell_parent_node_db)s: \\
  %(diskprint_cell_parent_node_db)s
	mkdir -p $$(dirname $@)
	rm -f $@
	cd $$(dirname $@) ; ln -s %(diskprint_cell_parent_node_abspath)s
""" % metadict
                    metadict["diskprint_cell_parent_node_pickle"] = "cell_parent/data_diskprints/paths_%(path)s/%(node_id)s.pickle" % metadict
                    rules_misc[metadict["cell_parent_node_pickle"]] = """\
%(cell_parent_node_pickle)s: \\
  %(diskprint_cell_parent_node_pickle)s
	mkdir -p $$(dirname $@)
	rm -f $@
	cd $$(dirname $@) ; ln -s %(diskprint_cell_parent_node_pickle)s
""" % metadict
                else:
                    rules_misc[metadict["cell_parent_node_db"]] = """\
%(cell_parent_node_db)s: \\
  %(registry_db)s \\
  cell_parent_db.py \\
  normalizer.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) cell_parent_db.py $(DEBUG_FLAG) %(normalize_flag)s %(registry_db)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                    rules_misc[metadict["cell_parent_node_pickle"]] = """\
%(cell_parent_node_pickle)s: \\
  %(cell_parent_node_db)s \\
  dump_parent_map.py
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) dump_parent_map.py $(DEBUG_FLAG) %(cell_parent_node_db)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                rules_dependency_listing[metadict["cell_parent_db_manifest_txt"]].append(metadict["cell_parent_node_db"])

            #Derive a term list database from each Registry single-state database.  Permutes with N grams path normalization (but saves many repeated computation steps when permuting with stop lists)..
            for n_grams in _n_grams:
                for node_id in sorted(node_registry_db[dataset].keys()):
                    metadict["node_id"] = node_id
                    metadict["n_grams"] = n_grams
                    if n_grams == "all":
                        metadict["n_grams_flag"] = ""
                    elif n_grams.startswith("last"):
                        metadict["n_grams_flag"] = "--last-n --n-gram-length=%s" % n_grams[-1]
                    else:
                        metadict["n_grams_flag"] = "--n-gram-length=%s" % n_grams
                    metadict["node_cell_parent_pickle"] = "cell_parent/data_%(dataset)s/paths_%(path)s/%(node_id)s.pickle" % metadict
                    metadict["node_n_gram_derivation_pickle"] = "n_gram_derivation/data_%(dataset)s/paths_%(path)s/n_grams_%(n_grams)s/%(node_id)s.pickle" % metadict
                    metadict["normalize_flag"] = "--normalize" if path=="normalized" else ""
                    metadict["registry_db"] = node_registry_db[dataset][node_id]
                    #Path dereferencing here is because of an odd behavior that arose in SQLite, where soft links with relative directory references weren't being handled correctly in the core SQLite library.  Absolute pathing is a hack around that bug.
                    metadict["registry_db_abspath"] = os.path.realpath(node_registry_db[dataset][node_id])
                    metadict["term_db"] = "term_db/data_%(dataset)s/paths_%(path)s/n_grams_%(n_grams)s/%(node_id)s.db" % metadict

                    #The training files can be soft-linked.
                    if dataset == "training":
                        metadict["diskprint_term_db"] = "term_db/data_diskprints/paths_%(path)s/n_grams_%(n_grams)s/%(node_id)s.db" % metadict
                        metadict["diskprint_term_db_abspath"] = os.path.join(os.path.realpath("."), metadict["term_db"])
                        rules_misc[metadict["term_db"]] = """\
%(term_db)s: \\
  %(diskprint_term_db)s
	mkdir -p $$(dirname $@)
	rm -f $@
	cd $$(dirname $@) ; ln -s %(diskprint_term_db_abspath)s
""" % metadict

                        metadict["diskprint_node_n_gram_derivation_pickle"] = "n_gram_derivation/data_diskprints/paths_%(path)s/n_grams_%(n_grams)s/%(node_id)s.pickle" % metadict
                        rules_misc[metadict["node_n_gram_derivation_pickle"]] = """\
%(node_n_gram_derivation_pickle)s: \\
  %(diskprint_node_n_gram_derivation_pickle)s
	mkdir -p $$(dirname $@)
	rm -f $@
	cd $$(dirname $@) ; ln -s %(diskprint_node_n_gram_derivation_pickle)s
""" % metadict
                    else:
                        rules_misc[metadict["term_db"]] = """\
%(term_db)s: \\
  %(node_n_gram_derivation_pickle)s \\
  reg_db_to_term_list.py \\
  %(registry_db)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) reg_db_to_term_list.py $(DEBUG_FLAG) %(normalize_flag)s %(node_n_gram_derivation_pickle)s %(registry_db_abspath)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                        rules_misc[metadict["node_n_gram_derivation_pickle"]] = """\
%(node_n_gram_derivation_pickle)s: \\
  %(node_cell_parent_pickle)s \\
  n_gram_derivation_pickle.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) n_gram_derivation_pickle.py $(DEBUG_FLAG) %(n_grams_flag)s %(node_cell_parent_pickle)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

    #Set up query-creating rules.
    for dataset in sorted(node_registry_db.keys()):
        for n_grams in _n_grams:
            for stop_list_n_gram_strategy in _stop_list_n_gram_strategies:
                for path in _paths:
                    for docs_by in _docs_bys:
                        for stop_list in _stop_lists:
                            metadict = dict()
                            metadict["dataset"] = dataset
                            metadict["docs_by"] = docs_by
                            metadict["path"] = path
                            metadict["stop_list"] = stop_list

                            metadict["n_grams"] = n_grams
                            if n_grams == "all":
                                metadict["n_grams_flag"] = ""
                            elif n_grams.startswith("last"):
                                metadict["n_grams_flag"] = "--last-n --n-gram-length=%s" % n_grams[-1]
                            else:
                                metadict["n_grams_flag"] = "--n-gram-length=%s" % n_grams
                            metadict["stop_list_n_gram_strategy"] = stop_list_n_gram_strategy
                            metadict["stop_list_n_gram_strategy_flag"] = "--stop-list-n-gram-strategy=%s" % stop_list_n_gram_strategy

                            if stop_list == "none":
                                metadict["stop_list_db_path"] = "stop_list/none.db"
                            elif stop_list == "bpi":
                                metadict["stop_list_db_path"] = "stop_list/data_training/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/%(stop_list)s.db" % metadict
                            else:
                                metadict["stop_list_db_path"] = "stop_list/data_training/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/%(stop_list)s.db" % metadict

                            if path == "normalized":
                                metadict["normalize_flag"] = "--normalize"
                            else:
                                metadict["normalize_flag"] = ""
 
                            metadict["query_list_file"] = "query/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/stop_list_%(stop_list)s/queries.txt" % metadict

                            for node_id in sorted(node_registry_db[dataset].keys()):
                                metadict["node_id"] = node_id
                                metadict["term_db"] = "term_db/data_%(dataset)s/paths_%(path)s/n_grams_%(n_grams)s/%(node_id)s.db" % metadict
                                metadict["query_db"] = "query/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/stop_list_%(stop_list)s/%(node_id)s.db" % metadict

                                if dataset == "training":
                                    #Training queries are just the diskprint queries, so soft-link to save work.
                                    metadict["diskprints_query_db_relpath"] = "query/data_diskprints/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/stop_list_%(stop_list)s/%(node_id)s.db" % metadict
                                    metadict["diskprints_query_db_abspath"] = os.path.join(os.path.realpath("."), metadict["diskprints_query_db_relpath"])
                                    rule = """\
%(query_db)s: \\
  %(diskprints_query_db_relpath)s
	mkdir -p $$(dirname $@)
	cd $$(dirname $@) ; rm -f $$(basename $@) ; ln -s %(diskprints_query_db_abspath)s
""" % metadict
                                else:
                                    #Write query-creating rule.
                                    rule = """\
%(query_db)s: \\
  %(stop_list_db_path)s \\
  stoplisted_query.py \\
  %(term_db)s \\
  vsm_set_theory_ops.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) stoplisted_query.py $(DEBUG_FLAG) %(stop_list_n_gram_strategy_flag)s %(stop_list_db_path)s %(term_db)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                                rules_misc[metadict["query_db"]] = rule
                                rules_dependency_listing[metadict["query_list_file"]].append(metadict["query_db"])
    _logger.debug("%d rules in rules_misc after defining query rules." % len(rules_misc))

    #Make stop list rules
    for n_grams in _n_grams:
        for stop_list_n_gram_strategy in _stop_list_n_gram_strategies:
            for path in _paths:
                metadict = dict()
                metadict["dataset"] = "training"
                metadict["n_grams"] = n_grams
                metadict["path"] = path
                metadict["normalize_flag"] = "--normalize" if path == "normalized" else ""
                #NOTE: The cell parent pickle to use will be the one for the diskprints, not the training data subset.  Stop lists will incorporate more entries than were in the training data.
                metadict["cell_parent_pickle"] = "cell_parent/data_diskprints/paths_%(path)s/cell_parent.pickle" % metadict
                if n_grams == "all":
                    metadict["n_gram_length_flags"] = ""
                    metadict["cell_parent_pickle_flag"] = ""
                elif n_grams.startswith("last"):
                    metadict["n_gram_length_flags"] = "--n-gram-length=%s --last-n" % n_grams[-1]
                    metadict["cell_parent_pickle_flag"] = "--cell-parent-pickle='%(cell_parent_pickle)s'" % metadict
                else:
                    metadict["n_gram_length_flags"] = "--n-gram-length=%s" % n_grams
                    metadict["cell_parent_pickle_flag"] = "--cell-parent-pickle='%(cell_parent_pickle)s'" % metadict
                metadict["stop_list_n_gram_strategy"] = stop_list_n_gram_strategy
                metadict["stop_list_n_gram_strategy_flag"] = "--stop-list-n-gram-strategy=%s" % stop_list_n_gram_strategy

                #baseline
                metadict["baseline_db"] = "stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/baseline.db" % metadict
                rules_misc[metadict["baseline_db"]] = """\
%(baseline_db)s: \\
  %(cell_parent_pickle)s \\
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \\
  n_grammer.py \\
  normalizer.py \\
  sequences/namedsequence.db \\
  stop_list_normalized.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) stop_list_normalized.py --baseline %(normalize_flag)s $(DEBUG_FLAG) %(cell_parent_pickle_flag)s %(n_gram_length_flags)s sequences/namedsequence.db diskprint_extraction_workflow_results/data_diskprints $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                #preinstalled
                metadict["preinstalled_db"] = "stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/preinstalled.db" % metadict
                rule = """\
%(preinstalled_db)s: \\
  %(cell_parent_pickle)s \\
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \\
  n_grammer.py \\
  normalizer.py \\
  sequences/namedsequence.db \\
  stop_list_normalized.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) stop_list_normalized.py --preinstalled %(normalize_flag)s $(DEBUG_FLAG) %(cell_parent_pickle_flag)s %(n_gram_length_flags)s sequences/namedsequence.db diskprint_extraction_workflow_results/data_diskprints $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                rules_misc[metadict["preinstalled_db"]] = rule

                #bp
                metadict["bp_db"] = "stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/bp.db" % metadict
                rule = """\
%(bp_db)s: \\
  glom_stop_lists.py \\
  stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/baseline.db \\
  stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/preinstalled.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) glom_stop_lists.py $(DEBUG_FLAG) $$(dirname $@)/_$$(basename $@) stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/{baseline,preinstalled}.db
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                rules_misc[metadict["bp_db"]] = rule

                for docs_by in _docs_bys:
                    #inconsistent
                    metadict["docs_by"] = docs_by
                    metadict["vsm"] = "vsm/sequences_repeated/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_inconsistent/stop_list_bp/vsm.pickle" % metadict
                    metadict["inconsistent_db"] = "stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/inconsistent.db" % metadict

                    rule = """\
%(inconsistent_db)s: \\
  TFIDFEngine.py \\
  stop_list_inconsistent.py \\
  %(vsm)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) stop_list_inconsistent.py $(DEBUG_FLAG) %(n_gram_length_flags)s %(vsm)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                    rules_misc[metadict["inconsistent_db"]] = rule

                    #bpi
                    metadict["bpi_db"] = "stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/bpi.db" % metadict
                    rule = """\
%(bpi_db)s: \\
  glom_stop_lists.py \\
  stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/baseline.db \\
  stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/inconsistent.db \\
  stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/preinstalled.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) glom_stop_lists.py $(DEBUG_FLAG) $$(dirname $@)/_$$(basename $@) stop_list/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/{baseline,docs_by_%(docs_by)s/inconsistent,preinstalled}.db
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                    rules_misc[metadict["bpi_db"]] = rule

    #Make VSM rules
    for sequence in _sequences:
        for n_grams in _n_grams:
            for stop_list_n_gram_strategy in _stop_list_n_gram_strategies:
                for path in _paths:
                    for docs_by in _docs_bys:
                        for combinator in _combinators:
                            for stop_list in _stop_lists:
                                metadict = dict()
                                metadict["sequence"] = sequence
                                metadict["path"] = path
                                metadict["docs_by"] = docs_by
                                metadict["combinator"] = combinator
                                metadict["stop_list"] = stop_list

                                metadict["cell_parent_pickle"] = "cell_parent/data_training/paths_%(path)s/cell_parent.pickle" % metadict
                                metadict["n_grams"] = n_grams
                                if n_grams == "all":
                                    metadict["n_grams_flag"] = ""
                                    metadict["cell_parent_dependency"] = ""
                                    metadict["cell_parent_flag"] = ""
                                else:
                                    metadict["cell_parent_dependency"] = metadict["cell_parent_pickle"]
                                    metadict["cell_parent_flag"] = "--cell-parent-pickle=%(cell_parent_pickle)s" % metadict
                                    if n_grams.startswith("last"):
                                        metadict["n_grams_flag"] = "--last-n --n-gram-length=%s" % n_grams[-1]
                                    else:
                                        metadict["n_grams_flag"] = "--n-gram-length=%s" % n_grams
                                metadict["stop_list_n_gram_strategy"] = stop_list_n_gram_strategy
                                metadict["stop_list_n_gram_strategy_flag"] = "--stop-list-n-gram-strategy=%s" % stop_list_n_gram_strategy

                                if stop_list == "none":
                                    metadict["stop_list_db_path"] = "stop_list/none.db"
                                elif stop_list == "bpi":
                                    metadict["stop_list_db_path"] = "stop_list/data_training/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/%(stop_list)s.db" % metadict
                                else:
                                    metadict["stop_list_db_path"] = "stop_list/data_training/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/%(stop_list)s.db" % metadict
    
                                metadict["combinator_flag"] = "--" + combinator
                                metadict["normalize_flag"] = "--normalize" if path == "normalized" else ""
    
                                if docs_by == "app":
                                    metadict["docs_by_flag"] = "--by-app"
                                elif docs_by == "osapp":
                                    metadict["docs_by_flag"] = "--by-osapp"

                                metadict["vsm_file"] = "vsm/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/vsm.pickle" % metadict

                                rules_misc[metadict["vsm_file"]] = """\
%(vsm_file)s: \\
  TFIDFEngine.py \\
  %(cell_parent_dependency)s n_grammer.py \\
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \\
  sequences/namedsequence.db \\
  slice.db \\
  %(stop_list_db_path)s \\
  stoplisted_query.py \\
  vsm_set_theory_ops.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) vsm_set_theory_ops.py $(DEBUG_FLAG) %(n_grams_flag)s %(stop_list_n_gram_strategy_flag)s %(combinator_flag)s --prefix %(sequence)s %(docs_by_flag)s %(normalize_flag)s %(cell_parent_flag)s %(stop_list_db_path)s sequences/namedsequence.db slice.db diskprint_extraction_workflow_results/data_diskprints $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                                #Make some statistics about the VSM's signatures
                                metadict["vsm_stats"] = "signature_statistics/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/signature_statistics.db" % metadict
                                rule = """\
%(vsm_stats)s: \\
  signature_statistics.py \\
  %(vsm_file)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) signature_statistics.py $(DEBUG_FLAG) %(vsm_file)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                                rules_misc[metadict["vsm_stats"]] = rule

                                #After this point, the inconsistent steps are not needed.
                                if combinator == "inconsistent":
                                    continue

                                #Make manifest of all of the VSM signature statistics dbs for later rollup.
                                rules_dependency_listing["signature_statistics_manifest.txt"].append(metadict["vsm_stats"])

                                #Build query results (each corpus) against VSMs
                                for dataset in _datasets:
                                    metadict["dataset"] = dataset
                                    metadict["query_list_file"] = "query/data_%(dataset)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/stop_list_%(stop_list)s/queries.txt" % metadict
                                    metadict["search_scores_pickle_manifest"] = "search_scores/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/pickle_manifest.txt" % metadict
                                    rules_misc[metadict["search_scores_pickle_manifest"]] = """\
%(search_scores_pickle_manifest)s: \\
  TFIDFEngine.py \\
  %(query_list_file)s \\
  run_model_on_queries.py \\
  %(vsm_file)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) run_model_on_queries.py $(DEBUG_FLAG) %(vsm_file)s %(query_list_file)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                                    #Look up the scores of each query run against a model.  (This file has no influence from ground truth definitions.)
                                    metadict["evaluating_search_score_manifest"] = "search_scores/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/pickle_manifest.txt" % metadict

                                    for score_selector in _score_selectors:
                                        metadict["score_selector"] = score_selector
                                        for versions in _versions:
                                            metadict["versions"] = versions
                                            metadict["ground_truth_db"] = "ground_truth/data_%(dataset)s/docs_by_%(docs_by)s/versions_%(versions)s/ground_truth.db" % metadict

                                            #Build Signature Searchers and the extracted threshold dictionaries on only the training data.
                                            if dataset == "training":
                                                metadict["score_selector_flag"] = "--" + score_selector
                                                metadict["signature_searcher_file"] = "signature_searcher_training/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/versions_%(versions)s/score_selector_%(score_selector)s/signature_searcher.pickle" % metadict
                                                rules_misc[metadict["signature_searcher_file"]] = """\
%(signature_searcher_file)s: \\
  SignatureSearcher.py \\
  TFIDFEngine.py \\
  %(ground_truth_db)s \\
  %(search_scores_pickle_manifest)s \\
  train_SignatureSearcher.py \\
  %(vsm_file)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) train_SignatureSearcher.py $(DEBUG_FLAG) %(score_selector_flag)s %(ground_truth_db)s %(vsm_file)s %(search_scores_pickle_manifest)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                                                #Extract document threshold dictionaries (some analysis doesn't need the whole VSM included)
                                                metadict["threshold_file"] = "signature_searcher_thresholds/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/versions_%(versions)s/score_selector_%(score_selector)s/signature_searcher_thresholds.pickle" % metadict
                                                rules_misc[metadict["threshold_file"]] = """\
%(threshold_file)s: \\
  SignatureSearcher.py \\
  extract_threshold_dictionary.py \\
  %(signature_searcher_file)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) extract_threshold_dictionary.py $(DEBUG_FLAG) %(signature_searcher_file)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                                            #Evaluate signature searchers on each data set.
                                            metadict["evaluation_tuples_pickle"] = "signature_searcher_measuring/data_%(dataset)s/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/versions_%(versions)s/score_selector_%(score_selector)s/evaluation_tuples.pickle" % metadict
                                            #Use training threshold file
                                            metadict["threshold_file"] = "signature_searcher_thresholds/data_training/sequences_%(sequence)s/n_grams_%(n_grams)s/stop_list_n_gram_strategy_%(stop_list_n_gram_strategy)s/paths_%(path)s/docs_by_%(docs_by)s/combinator_%(combinator)s/stop_list_%(stop_list)s/versions_%(versions)s/score_selector_%(score_selector)s/signature_searcher_thresholds.pickle" % metadict
                                            rules_misc[metadict["evaluation_tuples_pickle"]] = """\
%(evaluation_tuples_pickle)s: \\
  %(evaluating_search_score_manifest)s \\
  %(ground_truth_db)s \\
  measure_SignatureSearcher.py \\
  %(threshold_file)s
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) measure_SignatureSearcher.py $(DEBUG_FLAG) %(ground_truth_db)s %(threshold_file)s %(evaluating_search_score_manifest)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                                            #Make manifest of all of the signature search evaluation pickles.
                                            rules_dependency_listing["signature_searcher_measurement_manifest.txt"].append(metadict["evaluation_tuples_pickle"])

    rule = """\
threshold_inspection.db: \\
  signature_searcher_measurement_manifest.txt \\
  inspect_thresholds.py
	rm -f _$@
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) inspect_thresholds.py $(DEBUG_FLAG) signature_searcher_measurement_manifest.txt _$@
	mv _$@ $@
"""
    rules_misc["threshold_inspection.db"] = rule

    for target in sorted(rules_dependency_listing.keys()):
        #Each rule ends with a mv command to make tracking work-to-do easier.
        rule_parts = ["%s:" % target]
        for dependency in sorted(rules_dependency_listing[target]):
            rule_parts.append(" \\\n  " + dependency)
        rule_parts.append("\n\trm -f $$(dirname $@)/__$$(basename $@)")
        rule_parts.append("\n\trm -f $$(dirname $@)/_$$(basename $@)")
        for dependency in sorted(rules_dependency_listing[target]):
            rule_parts.append("\n\techo %s >> $$(dirname $@)/__$$(basename $@)" % dependency)
        rule_parts.append("\n\tsort $$(dirname $@)/__$$(basename $@) > $$(dirname $@)/_$$(basename $@) && rm $$(dirname $@)/__$$(basename $@)")
        rule_parts.append("\n\tmv $$(dirname $@)/_$$(basename $@) $@")
        rule_parts.append("\n")
        rules_misc[target] = "".join(rule_parts)

    with open(args.output_mk, "w") as fh:
        fh.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
GTIME ?= /opt/local/bin/gtime
SHELL = /bin/bash
PYTHON3 ?= python3.4

all: \\
  searcher_scores.db

.PHONY: \\
  extra \\
  misc

extra: \\
  threshold_inspection.db

misc:""")
        for target in sorted(rules_misc.keys()):
            fh.write(" \\\n  %s" % target)
        fh.write("\n")

        for target in sorted(rules_misc.keys()):
            fh.write("\n")
            fh.write(rules_misc[target])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("sequences_db")
    parser.add_argument("experiment1_node_list")
    parser.add_argument("dewf_results_diskprints")
    parser.add_argument("dewf_results_evaluation")
    parser.add_argument("dewf_results_m57")
    parser.add_argument("output_mk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
