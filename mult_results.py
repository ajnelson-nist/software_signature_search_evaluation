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
This script generates a Makefile for targets that were easier to define with looping macros.
"""

__version__ = "0.1.0"

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import SignatureSearcher_ppp

DIST_TARGETS = set([
  "cumulative_histogram_evaluation_f1.pdf",
  "cumulative_histogram_evaluation_precision.pdf",
  "cumulative_histogram_evaluation_recall.pdf",
  "cumulative_histogram_m57_f1.pdf",
  "cumulative_histogram_m57_precision.pdf",
  "cumulative_histogram_m57_recall.pdf",
  "overview_scatter_hist/subset_all/data_evaluation/precrec.pdf",
  "overview_scatter_hist/subset_all/data_m57/precrec.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/f1nratio.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/f1num.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/precnratio.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/precnum.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/precrec.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/recnratio.pdf",
  "overview_scatter_hist/subset_nocontrol/data_evaluation/recnum.pdf",
  "penultimate_f1_evaluation.tex",
  "penultimate_f1_m57.tex",
  "penultimate_precision_evaluation.tex",
  "penultimate_precision_m57.tex",
  "penultimate_recall_evaluation.tex",
  "penultimate_recall_m57.tex",
  "perfect_searchers_f1.tsv",
  "perfect_searchers_precision.tsv",
  "perfect_searchers_precision_docs_by.tex",
  "perfect_searchers_precision_n_grams.tex",
  "perfect_searchers_recall.tsv",
  "precision_recall_scatter/subset_all/data_evaluation/scatter_by_sequences.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_docs_by.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_n_grams.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_n_grams_collapsed.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_paths.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_combinator.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_score_selector.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_sequences.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_stop_list.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_stop_list_n_gram_strategy.pdf",
  "precision_recall_scatter/subset_nocontrol/data_evaluation/scatter_by_versions.pdf",
  "scatter_f1_between_corpora.pdf",
  "scatter_precision_between_corpora.pdf",
  "scatter_recall_between_corpora.pdf",
  "searcher_scores_pair_grids/subset_all/data_evaluation/all.pdf",
  "searcher_scores_pair_grids/subset_all/data_evaluation/for_talk_1x4.pdf",
  "searcher_scores_pair_grids/subset_all/data_evaluation/for_talk_2x5.pdf",
  "searcher_scores_pair_grids/subset_all/data_evaluation/for_talk_3x4.pdf",
  "searcher_scores_pair_grids/subset_all/data_m57/all.pdf",
  "searcher_scores_pair_grids/subset_all/data_m57/for_talk_1x4.pdf",
  "searcher_scores_pair_grids/subset_all/data_m57/for_talk_2x5.pdf",
  "searcher_scores_pair_grids/subset_all/data_m57/for_talk_3x4.pdf",
  "searcher_scores_pair_grids/subset_nocontrol/data_evaluation/all.pdf",
  "searcher_scores_pair_grids/subset_nocontrol/data_m57/all.pdf",
  "top_n/by_f1/docs_by_app_evaluation.tex",
  "top_n/by_f1/docs_by_app_m57.tex",
  "top_n/by_f1/docs_by_osapp_evaluation.tex",
  "top_n/by_f1/docs_by_osapp_m57.tex",
  "top_n/by_f1/ngc_ng_evaluation.tex",
  "top_n/by_f1/ngc_ng_m57.tex",
  "top_n/by_f1/ngc_wp_evaluation.tex",
  "top_n/by_f1/ngc_wp_m57.tex",
  "top_n/by_precision/docs_by_app_evaluation.tex",
  "top_n/by_precision/docs_by_app_m57.tex",
  "top_n/by_precision/docs_by_osapp_evaluation.tex",
  "top_n/by_precision/docs_by_osapp_m57.tex",
  "top_n/by_precision/ngc_ng_m57.tex",
  "top_n/by_precision/ngc_ng_evaluation.tex",
  "top_n/by_precision/ngc_wp_evaluation.tex",
  "top_n/by_precision/ngc_wp_m57.tex",
  "top_n/by_recall/docs_by_app_evaluation.tex",
  "top_n/by_recall/docs_by_app_m57.tex",
  "top_n/by_recall/docs_by_osapp_evaluation.tex",
  "top_n/by_recall/docs_by_osapp_m57.tex",
  "top_n/by_recall/ngc_ng_evaluation.tex",
  "top_n/by_recall/ngc_ng_m57.tex",
  "top_n/by_recall/ngc_wp_evaluation.tex",
  "top_n/by_recall/ngc_wp_m57.tex"
])

def main():
    #Key: Target file.
    #Value: Makefile rule text.
    rules = dict()

    rule = """\
doc_summary_stats.db: \\
  doc_performance.db \\
  rank_doc_fp.sql \\
  searcher_scores.db
	rm -f _$@
	sqlite3 _$@ < rank_doc_fp.sql
	mv _$@ $@
"""
    rules["doc_summary_stats.db"] = rule

    for metric in ["Precision", "Recall", "F1"]:
        metadict = dict()
        metadict["metric"] = metric
        metadict["variable"] = metric.lower()
        metadict["scatter_between_pdf"] = "scatter_%(variable)s_between_corpora.pdf" % metadict
        rules[metadict["scatter_between_pdf"]] = """\
%(scatter_between_pdf)s: \\
  PY3_MATPLOTLIB \\
  scatter_metric_between_corpora.py \\
  searcher_scores.db
	rm -f _$@
	$(PYTHON3) scatter_metric_between_corpora.py $(DEBUG_FLAG) searcher_scores.db %(metric)s _$@
	mv _$@ $@
""" % metadict

        metadict["perfect_searchers_metric_sql"] = "perfect_searchers_%(variable)s.sql" % metadict
        rules[metadict["perfect_searchers_metric_sql"]] = """\
%(perfect_searchers_metric_sql)s: \\
  perfect_searchers_metric.sql.in
	rm -f _$@
	sed -e 's/%%METRIC%%/%(variable)s/g' $< > _$@
	mv _$@ $@
""" % metadict

        metadict["perfect_searchers_metric_tsv"] = "perfect_searchers_%(variable)s.tsv" % metadict
        rules[metadict["perfect_searchers_metric_tsv"]] = """\
%(perfect_searchers_metric_tsv)s: \\
  %(perfect_searchers_metric_sql)s \\
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@
""" % metadict

        for breakout_variable in ["docs_by", "n_grams"]:
            metadict["breakout_variable"] = breakout_variable
            metadict["perfect_searchers_metric_breakout_sql"] = "perfect_searchers_%(variable)s_%(breakout_variable)s.sql" % metadict
            rules[metadict["perfect_searchers_metric_breakout_sql"]] = """\
%(perfect_searchers_metric_breakout_sql)s: \\
  perfect_searchers_metric_breakout.sql.in
	rm -f _$@
	sed -e 's/%%METRIC%%/%(variable)s/g' $< | sed -e 's/%%BREAKOUT%%/%(breakout_variable)s/g' > _$@
	mv _$@ $@
""" % metadict
            metadict["perfect_searchers_metric_breakout_tex"] = "perfect_searchers_%(variable)s_%(breakout_variable)s.tex" % metadict
            rules[metadict["perfect_searchers_metric_breakout_tex"]] = """\
%(perfect_searchers_metric_breakout_tex)s: \\
  %(perfect_searchers_metric_breakout_sql)s \\
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@
""" % metadict

    for dataset in ["training", "evaluation", "m57"]:
        metadict = dict()

        for variable in ["precision", "recall", "f1"]:
            metadict["dataset"] = dataset
            metadict["variable"] = variable
            metadict["variable_label"] = {
              "precision": "Precision",
              "recall": "Recall",
              "f1": "F1"
            }[variable]

            #Make cumulative histograms
            metadict["target_file"] = "cumulative_histogram_%(dataset)s_%(variable)s.pdf" % metadict
            rule = """\
%(target_file)s: \\
  cumulative_histogram.py \\
  searcher_scores.db
	rm -f _$@
	$(PYTHON3) cumulative_histogram.py $(DEBUG_FLAG) searcher_scores.db %(dataset)s %(variable)s "%(variable_label)s" _$@
	mv _$@ $@
""" % metadict
            rules[metadict["target_file"]] = rule

            #Note next-to-last scores (but not for training data)
            if dataset != "training":
                rule = """\
penultimate_%(variable)s_%(dataset)s.tex: \\
  penultimate_%(variable)s_%(dataset)s.sql \\
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@
""" % metadict
                rules["penultimate_%(variable)s_%(dataset)s.tex" % metadict] = rule

            #Make threshold inspection
            metadict["threshold_scatter"] = "threshold_scatter/data_%(dataset)s/threshold_%(variable)s_scatter.png" % metadict
            rule = """\
%(threshold_scatter)s: \\
  scatter_thresholds.py \\
  threshold_inspection.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) scatter_thresholds.py $(DEBUG_FLAG) threshold_inspection.db %(dataset)s %(variable)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
            rules[metadict["threshold_scatter"]] = rule

        for subset in ["all", "nocontrol"]:
            metadict["subset"] = subset
            metadict["subset_flag"] = "--subset=%(subset)s" % metadict

            rule = """\
searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/all.pdf: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) searcher_scores_pair_grid.py $(DEBUG_FLAG) --big-font %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
            rules["searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/all.pdf" % metadict] = rule

            for out_format in ["pdf", "png"]:
                metadict["out_format"] = out_format
                rules["searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/for_poster_20150513.%(out_format)s" % metadict] = """\
searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/for_poster_20150513.%(out_format)s: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  poster_searcher_scores_pair_grid.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) poster_searcher_scores_pair_grid.py $(DEBUG_FLAG) --out-format=%(out_format)s %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                for grid in ["1x4", "2x5", "3x4"]:
                    metadict["grid"] = grid
                    rules["searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/for_talk_%(grid)s.%(out_format)s" % metadict] = """\
searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/for_talk_%(grid)s.%(out_format)s: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py \\
  talk_searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) talk_searcher_scores_pair_grid.py $(DEBUG_FLAG) --out-format=%(out_format)s --grid-size=%(grid)s %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                breakout_vars = [key for key in SignatureSearcher_ppp.var_fs_dir_to_pretty_header.keys()]
                for breakout_var in sorted(breakout_vars):
                    metadict["var_fs"] = breakout_var

                    metadict["pair_grid_file"] = "searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/inspect_%(var_fs)s.%(out_format)s" % metadict
                    rules[metadict["pair_grid_file"]] = """\
%(pair_grid_file)s: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) searcher_scores_pair_grid.py $(DEBUG_FLAG) --big-font --g-var="%(var_fs)s" %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                    if breakout_var == "n_grams":
                        metadict["pair_grid_file_ngc"] = "searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/inspect_%(var_fs)s_collapsed.%(out_format)s" % metadict
                        rules[metadict["pair_grid_file_ngc"]] = """\
%(pair_grid_file_ngc)s: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) searcher_scores_pair_grid.py $(DEBUG_FLAG) --big-font --g-var="%(var_fs)s" --collapse-n-grams %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict

                for upper_right in ["non", "only"]:
                    metadict["upper_right"] = upper_right
                    metadict["target"] = "searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/upper_right_%(upper_right)s.%(out_format)s" % metadict
                    rule = """\
%(target)s: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) searcher_scores_pair_grid.py $(DEBUG_FLAG) --upper-right=%(upper_right)s --out-format=%(out_format)s %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                    rules[metadict["target"]] = rule

                    metadict["target2"] = "searcher_scores_pair_grids/subset_%(subset)s/data_%(dataset)s/upper_right_%(upper_right)s_inspect_%(var_fs)s.%(out_format)s" % metadict
                    rule = """\
%(target2)s: \\
  PY3_MATPLOTLIB \\
  SignatureSearcher_ppp.py \\
  searcher_scores.db \\
  searcher_scores_pair_grid.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) searcher_scores_pair_grid.py $(DEBUG_FLAG) --upper-right=%(upper_right)s --out-format=%(out_format)s --g-var="%(var_fs)s" %(subset_flag)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                    rules[metadict["target2"]] = rule

        for subset in ["all", "nocontrol"]:
            metadict["subset"] = subset
            metadict["subset_flag"] = "--subset=%(subset)s" % metadict

            #Make non-breakout scatter plot of precision-recall, with histograms
            for axes_pair in ["precrec","f1num","f1nratio","precnum","precnratio","recnum","recnratio"]:
                metadict["axes_pair"] = axes_pair
                metadict["overview_scatter_hist_pdf"] = "overview_scatter_hist/subset_%(subset)s/data_%(dataset)s/%(axes_pair)s.pdf" % metadict
                rule = """\
%(overview_scatter_hist_pdf)s: \\
  overview_scatter_hist.py \\
  searcher_scores.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) overview_scatter_hist.py $(DEBUG_FLAG) %(subset_flag)s searcher_scores.db %(dataset)s %(axes_pair)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                rules[metadict["overview_scatter_hist_pdf"]] = rule

            #Make breakout scatter plots of precision-recall
            for breakout_variable in sorted(SignatureSearcher_ppp.var_fs_dir_to_pretty_header.keys()):
                metadict["breakout_variable"] = breakout_variable
                for out_format in ["png", "pdf"]:
                    metadict["pr_scatter_out_format"] = out_format
                    metadict["pr_scatter_out_format_flag"] = "--out-format=" + out_format
                    metadict["pr_scatter"] = "precision_recall_scatter/subset_%(subset)s/data_%(dataset)s/scatter_by_%(breakout_variable)s.%(pr_scatter_out_format)s" % metadict
                    rule = """\
%(pr_scatter)s: \\
  PY3_MATPLOTLIB \\
  scatter_plot.py \\
  searcher_scores.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) scatter_plot.py $(DEBUG_FLAG) %(pr_scatter_out_format_flag)s %(subset_flag)s --breakout=%(breakout_variable)s searcher_scores.db %(dataset)s $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                    rules[metadict["pr_scatter"]] = rule

    top_n_var_dict = dict()
    top_n_var_dict["docs_by_app"] = ("docs_by", "app")
    top_n_var_dict["docs_by_osapp"] = ("docs_by", "osapp")
    top_n_var_dict["ngc_ng"] = ("n_grams_collapsed", "N-gram")
    top_n_var_dict["ngc_wp"] = ("n_grams_collapsed", "Whole path")
    for top_n in sorted(top_n_var_dict.keys()):
        metadict = dict()

        metadict["top_n"] = top_n
        metadict["top_n_var"] = top_n_var_dict[top_n][0]
        metadict["top_n_val"] = top_n_var_dict[top_n][1]

        metadict["out_tex"] = "top_n/by_f1/%(top_n)s.tex" % metadict
        metadict["in_sql"] = "top_n/by_f1/%(top_n)s.sql" % metadict

        rule = """\
%(out_tex)s: \\
  %(in_sql)s \\
  searcher_scores.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	sqlite3 searcher_scores.db < $< > $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
        rules[metadict["out_tex"]] = rule

        for rank_variable in ["precision", "recall", "f1"]:
            for put_first in ["evaluation", "m57"]:
                #Make the vs. M57 comparisons
                metadict["rank_variable"] = rank_variable
                metadict["put_first"] = put_first
                metadict["out_tex"] = "top_n/by_%(rank_variable)s/%(top_n)s_%(put_first)s.tex" % metadict
                metadict["in_sql"] = "top_n/by_%(rank_variable)s/%(top_n)s_%(put_first)s.sql" % metadict

                rule = """\
%(in_sql)s: \\
  top_n_m57_generator.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) $< "%(rank_variable)s" "%(put_first)s" "%(top_n_var)s" "%(top_n_val)s" > $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                rules[metadict["in_sql"]] = rule

                rule = """\
%(out_tex)s: \\
  %(in_sql)s \\
  response_percentiles.db \\
  searcher_scores.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	sqlite3 searcher_scores.db < $< > $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@
""" % metadict
                rules[metadict["out_tex"]] = rule

    with open(args.out_mk, "w") as out_fh:
        out_fh.write("""\
#!/usr/bin/make -f

DEBUG_FLAG ?=
PYTHON3 ?= python3.4
SHELL = /bin/bash

all: dist

.PHONY: dist extra

dist:""")
        for target in sorted(rules.keys()):
            if target in DIST_TARGETS:
                out_fh.write(" \\\n  %s" % target)
        out_fh.write("\n")

        out_fh.write("\n")
        out_fh.write("extra:")
        for target in sorted(rules.keys()):
            if not target in DIST_TARGETS:
                out_fh.write(" \\\n  %s" % target)
        out_fh.write("\n")

        for target in sorted(rules.keys()):
            out_fh.write("\n")
            out_fh.write(rules[target])

    missing_targets = DIST_TARGETS - set(rules.keys())
    if len(missing_targets) != 0:
        _logger.error("Need to define code to reach these targets:")
        for target in missing_targets:
            _logger.error("* %r" % target)
        raise NotImplementedError("Some targets are not implemented in the script yet.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("out_mk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
