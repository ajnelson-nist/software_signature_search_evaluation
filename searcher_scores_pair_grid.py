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

# Example source:
#   http://stanford.edu/~mwaskom/software/seaborn/examples/paired_pointplots.html

__version__ = "0.6.2"

import logging
import os
import sqlite3

_logger = logging.getLogger(os.path.basename(__file__))

import pandas as pd
import seaborn as sns

import SignatureSearcher_ppp

_x_vars = {
  "docs_by": ["app", "osapp"],
  "versions": ["distinct", "grouped"],
  "paths": ["raw", "normalized"],
  "n_grams": ["all", "1", "2", "3", "last1", "last2", "last3"],
  "n_grams_collapsed": ["all", "n", "lastn"],
  "stop_list_n_gram_strategy": ["raw_filter", "n_gram_blacklist", "n_gram_threshold"],
  "sequences": ["installclose", "repeated", "experiment1"],
  "combinator": ["intersection", "summation", "sumint"],
  "stop_list": ["none", "baseline", "bp", "bpi"],
  "score_selector": ["min", "avg", "max"],
  "dataset": ["training", "evaluation", "m57"]
}
assert set(_x_vars.keys()) == set(SignatureSearcher_ppp.var_fs_dir_to_pretty_header.keys())
_x_vars_order = [
  "docs_by",
  "versions",
  "paths",
  "n_grams",
  "stop_list_n_gram_strategy",
  "sequences",
  "combinator",
  "stop_list",
  "score_selector",
  "dataset"
]

_y_vars = {"num_runs", "f1"}

def make_pair_grid(x_vars, y_vars):
    conn = sqlite3.connect(args.in_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #The df variable definition is going to get a big bundle of order-maintaining code.  There doesn't seem to be a clear way to ensure a value order in the nested sns.pointplot call, except for manipulating encounter order in the dataframe.
    #  Reference: <https://github.com/mwaskom/seaborn/issues/361#issuecomment-68148278>
    #    It's possible I missed something later in that thread.
    for x_var in x_vars:
        _logger.debug("Creating order table for %r." % x_var)
        cursor.execute("""\
CREATE TEMPORARY TABLE temp_value_order_%s (
  %s TEXT,
  value_order INTEGER
);""" % (x_var, x_var))
        #Pull value order from data structure that is global in this module.
        for (x_var_value_no, x_var_value) in enumerate(_x_vars[x_var]):
            cursor.execute("INSERT INTO temp_value_order_%s VALUES(?,?);" % x_var, (x_var_value, x_var_value_no))

    extra_tables_parts = []
    extra_where_clause_parts = []
    order_by_clause_parts = []
    for x_var in x_vars:
        extra_tables_parts.append(",\n  temp_value_order_%s" % x_var)
        extra_where_clause_parts.append(" AND\n  searchers_with_nonzerolen_doc_counts.%s = temp_value_order_%s.%s" % (x_var, x_var, x_var))
        order_by_clause_parts.append("temp_value_order_%s.value_order" % x_var)
    if args.subset == "nocontrol":
        extra_where_clause_parts.append(" AND\n  searchers_with_nonzerolen_doc_counts.sequences <> 'experiment1'")
    extra_tables = "".join(extra_tables_parts)
    extra_where_clause = "".join(extra_where_clause_parts)
    if len(order_by_clause_parts) == 0:
        order_by_clause = ""
    else:
        order_by_clause = "\nORDER BY\n  " + ",\n  ".join(order_by_clause_parts)
    #Also translate some variable value labels to break up long label lines and "left-pad" for consistent x axis label heights.  (xtick.major.pad had an unexpected effect.)
    sql = """\
SELECT
  searchers_with_nonzerolen_doc_counts.*,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.combinator = 'intersection' THEN 'intersection             '
    ELSE searchers_with_nonzerolen_doc_counts.combinator
  END AS combinator_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.docs_by = 'osapp' THEN 'osapp                      '
    ELSE searchers_with_nonzerolen_doc_counts.docs_by
  END AS docs_by_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.n_grams = 'last3' THEN 'last3                        '
    ELSE searchers_with_nonzerolen_doc_counts.n_grams
  END AS n_grams_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.paths = 'normalized' THEN 'normalized              '
    ELSE searchers_with_nonzerolen_doc_counts.paths
  END AS paths_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.sequences = 'installclose' THEN 'installclose              '
    ELSE searchers_with_nonzerolen_doc_counts.sequences
  END AS sequences_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.score_selector = 'max' THEN 'max                      '
    ELSE searchers_with_nonzerolen_doc_counts.score_selector
  END AS score_selector_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.stop_list = 'baseline' THEN 'baseline                  '
    ELSE searchers_with_nonzerolen_doc_counts.stop_list
  END AS stop_list_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.stop_list_n_gram_strategy = 'raw_filter' THEN 'raw filter'
    WHEN searchers_with_nonzerolen_doc_counts.stop_list_n_gram_strategy = 'n_gram_blacklist' THEN 'n-gram blacklist'
    WHEN searchers_with_nonzerolen_doc_counts.stop_list_n_gram_strategy = 'n_gram_threshold' THEN 'n-gram threshold'
    ELSE NULL
  END AS stop_list_n_gram_strategy_translated,

  CASE
    WHEN searchers_with_nonzerolen_doc_counts.versions = 'grouped' THEN 'grouped                '
    ELSE searchers_with_nonzerolen_doc_counts.versions
  END AS versions_translated

FROM
  searchers_with_nonzerolen_doc_counts%s
WHERE
  dataset = '%s'%s%s
;""" % (extra_tables, args.dataset, extra_where_clause, order_by_clause)
    _logger.debug("sql = %s." % sql)
    if args.subset == "nocontrol":
        cursor.execute("SELECT COUNT(*) AS tally FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%s' AND sequences <> 'experiment1';" % args.dataset)
    else:
        cursor.execute("SELECT COUNT(*) AS tally FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%s';" % args.dataset)
    row = cursor.fetchone()
    tally_without_big_clauses = row["tally"]
    _logger.debug("Without ordering clauses, the dataset %r provides %d rows." % (args.dataset, tally_without_big_clauses))
    df = pd.io.sql.read_sql(sql, conn)
    _logger.debug("len(df) = %r." % len(df))
    assert len(df) == tally_without_big_clauses #If this is wrong, there's probably a missing parameter value in the matrix at the top of the script.

    #Restrict analysis region if requested
    #C/o: <https://stackoverflow.com/a/11872393>
    if args.upper_right == "only":
        df = df[(df.precision >= 0.5) & (df.recall >= 0.5)]
    elif args.upper_right == "non":
        df = df[(df.precision < 0.5) & (df.recall < 0.5)]


    #Translate variable and value labels
    x_vars_translated = []
    for x_var in x_vars:
        if x_var == "score_selector":
            x_var_translated = "Score\nselector"
        elif x_var == "stop_list_n_gram_strategy":
            x_var_translated = "Stop list\nn-gram\nstrategy"
        elif x_var == "versions":
            x_var_translated = "Version\ngrouping"
        else:
            x_var_translated = SignatureSearcher_ppp.var_fs_dir_to_pretty_header[x_var]

        if args.big_font:
            df[x_var_translated] = df[x_var + "_translated"]
        else:
            df[x_var_translated] = df[x_var]
        x_vars_translated.append(x_var_translated)

    #Set up keyword arguments
    pair_grid_kwargs = {
      "y_vars": y_vars,
      "x_vars": x_vars_translated
    }

    if args.g_var:
        pair_grid_kwargs["hue"] = args.g_var
        if args.collapse_n_grams and args.g_var == "n_grams":
            pair_grid_kwargs["hue"] = "n_grams_collapsed"

    #Up font size if requested
    #https://stanford.edu/~mwaskom/software/seaborn/generated/seaborn.set.html
    #https://stanford.edu/~mwaskom/software/seaborn/generated/seaborn.set_style.html
    if args.big_font:
        sns.set(font_scale=1.9)
        #sns.set_style({"xtick.major.pad": 80}) #TODO What I'd like is for this to handle left-padding for all of the labels, but it instead pads everything away from the axis label (regardless of tick label rotation), which causes a vertical squish on the grid instead of axis label alignment.  Seaborn bug?  Until resolved, the whitespace hack will have to do.
        xtick_rotation_angle = 270
        ylabel_rotation_angle = 270
    else:
        xtick_rotation_angle = 30
        ylabel_rotation_angle = 0
        ylabel_pad = None

    g = sns.PairGrid(df, **pair_grid_kwargs)

    #(ci:None -> Turn off confidence intervals)
    g.map(sns.pointplot, ci=None)
    #g.set(ylim=(0,1))

    #Adjust axes
    #  C/o: <https://stackoverflow.com/a/25213438>
    #    Though, that answer got the axes[] indices transposed.
    #_logger.debug("dir(g.axes[0,0]) = %r." % dir(g.axes[0,0]))
    for i in range(len(y_vars)):
        y_var_pcased = y_vars[i][0].upper() + y_vars[i][1:]
        g.axes[i,0].set_ylim(-0.05,1.05)
        kwargs = {"rotation": ylabel_rotation_angle}
        if args.big_font:
            #labelpad c/o: <https://stackoverflow.com/a/6406750>.  Existence is not obvious from pyplot documentation: <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.ylabel>.
            kwargs["labelpad"] = 40
        g.axes[i,0].set_ylabel(y_var_pcased, **kwargs)
    #Set xtick label rotation for long labels
    #  C/o: <https://stackoverflow.com/a/14854007>
    for i in range(len(x_vars)):
        labels = g.axes[-1,i].get_xticklabels()
        #_logger.debug("x_vars[i] = %r." % x_vars[i])
        #_logger.debug("labels = %r." % labels)
        #if args.debug:
        #    for (label_no, label) in enumerate(labels):
        #        _logger.debug("label[%d] = %r." % (label_no, label))
        #        #_logger.debug("dir(label) = %r." % dir(label))
        #        _logger.debug("label.get_label() = %r." % label.get_label())
        #        _logger.debug("label.get_text() = %r." % label.get_text()) # <-- This is the text of the label.
        g.axes[-1,i].set_xticklabels(labels, rotation=xtick_rotation_angle, ha='right')

    #if args.g_var:
    #    _logger.debug("g.hue_names = %r." % g.hue_names)
    #    _logger.debug("dir(g) = %r." % dir(g))
    #    _logger.debug("g._legend_data = %r." % g._legend_data)
    #    _logger.debug("g._legend_out = %r." % g._legend_out)
    #    g.add_legend(None, None, g.hue_names)

    g.savefig(args.out_file, format=args.out_format)

def main():
    #TODO There is a bug with legend populating in Seaborn 0.5.1.  The hack to identify color is to not filter out the breakout variable.
    ##Set up X variables list
    #x_vars_filtered = [var for var in sorted(_x_vars.keys()) if var not in {"Dataset", args.g_var}]
    ignore_set = {"dataset", "threshold_trainers"}
    x_vars_filtered = [var for var in _x_vars_order if var not in ignore_set]
    if args.collapse_n_grams:
        if "n_grams" in x_vars_filtered:
            i = x_vars_filtered.index("n_grams")
            x_vars_filtered[i] = "n_grams_collapsed"

    y_vars = ["precision", "recall", "f1"]

    make_pair_grid(x_vars_filtered, y_vars)

#Expose argument parser as module object
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument("--big-font", action="store_true")
parser.add_argument("--collapse-n-grams", action="store_true")
parser.add_argument("--g-var", choices=sorted(_x_vars.keys()))
parser.add_argument("--out-format", default="pdf")
parser.add_argument("--upper-right", choices=["only","non"], help="Restrict analysis to only upper-right quadrant of precision-recall space.")
parser.add_argument("--subset", choices={"all", "nocontrol"})
parser.add_argument("in_db")
parser.add_argument("dataset")
parser.add_argument("out_file")

if __name__ == "__main__":
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
