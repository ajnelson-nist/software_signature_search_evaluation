#!/usr/bin/env python3

# For changes made after April 1, 2016:
#
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
Simple demo of a scatter plot.

Sample code from:
http://matplotlib.org/examples/shapes_and_collections/scatter_demo.html

Legend code c/o:
http://stackoverflow.com/a/17412294
http://matplotlib.org/users/legend_guide.html

May want to try:
http://pandas.pydata.org/pandas-docs/stable/visualization.html#scatter-plot
"""

__version__ = "0.4.1"

import logging
import os
import sqlite3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

_logger = logging.getLogger(os.path.basename(__file__))

import SignatureSearcher_ppp

def main():
    ##Dummy up data
    #N = 50
    #x = np.random.rand(N)
    #y = np.random.rand(N)
    #_logger.debug("type(x) = %r." % type(x))

    #Load data
    conn = sqlite3.connect(args.in_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if args.subset == "all":
        cursor.execute("SELECT * FROM searchers WHERE dataset=?;", (args.dataset,))
    elif args.subset == "nocontrol":
        cursor.execute("SELECT * FROM searchers WHERE dataset=? AND sequences <> 'experiment1';", (args.dataset,))
    else:
        raise NotImplementedError("args.subset value not implemented: %r." % args.subset)

    #Collapse the seven-value n-grams.
    rows = []
    for row in cursor:
        drow = {key:row[key] for key in row.keys()}
        drow["n_grams_collapsed"] = {
          "all":"all",
          "1":"n",
          "2":"n",
          "3":"n",
          "last1":"last_n",
          "last2":"last_n",
          "last3":"last_n"
        }[row["n_grams"]]
        rows.append(drow)
    _logger.debug("Read %d rows." % len(rows))
    _logger.debug("First row: %r." % rows[0])
    _logger.debug("Keys of first row: %r." % [key for key in sorted(rows[0].keys())])

    subset_rows = [row for row in rows if not None in (row["precision"], row["recall"])]
    _logger.debug("Reduced to %d rows with non-null precision and recall." % len(subset_rows))
    _logger.debug("First row: %r." % rows[0])
    _logger.debug("Keys of first row: %r." % [key for key in sorted(rows[0].keys())])

    if args.breakout:
        #Make room for legend (before assigning axis labels)
        #  C/o: https://stackoverflow.com/a/9651897
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.75])

    plt.xlabel("Recall")
    plt.ylabel("Precision")

    #Deal with seven colors differently.
    if args.breakout and args.breakout == "n_grams":
        #Colors c/o: <https://stackoverflow.com/a/29676907>
        colors = ["forestgreen", "teal", "lightseagreen", "b", "firebrick", "orangered", "darkorange"]
        #Markers reference: http://matplotlib.org/examples/lines_bars_and_markers/marker_reference.html
        markers = ["+", "1", "2", ".", "x", "3", "4"]
    else:
        colors = ["b", "c", "y", "m", "r", "g", "k"]
        markers = ["x", "+", "1", "2", ".", "h", mpl.markers.CARETDOWN]

    if args.breakout:
        breakout_pretty = SignatureSearcher_ppp.var_fs_dir_to_pretty_header[args.breakout]

        plt.title("Precision-Recall scatter plot\nBreakout: %s\n\n" % breakout_pretty)
        breakout_values = set(row[args.breakout] for row in rows) #(Note that this is NOT the subset)
        _logger.debug("breakout_values = %r." % breakout_values)
        debug_legend_labels = []
        breakout_scatters = []

        _logger.debug("%d breakout values to plot." % len(breakout_values))
        for (breakout_value_no, breakout_value) in enumerate(sorted(breakout_values)):
            _logger.debug("Plotting breakout value %r." % breakout_value)
            xs = []
            ys = []
            for row in subset_rows:
                if row[args.breakout] != breakout_value:
                    continue
                xs.append(row["recall"])
                ys.append(row["precision"])

            debug_legend_labels.append(breakout_value)

            breakout_scatters.append(
              plt.scatter(
                xs,
                ys,
                s=60,
                color=colors[breakout_value_no],
                marker=markers[breakout_value_no],
                label=breakout_value
              )
            )
        _logger.debug("Creating legend.")
        _logger.debug("debug_legend_labels: %r." % debug_legend_labels)
        plt.legend(
          scatterpoints=1,
          loc='upper left',
          #mode="expand",
          ncol=10,
          fontsize=10,
          bbox_to_anchor=(0.0, 0.99, 1.0, 0.102),
          borderaxespad=0.
        )
    else:
        plt.title("Precision-Recall scatter plot\nBreakout: None")
        xs = [row["recall"] for row in subset_rows]
        ys = [row["precision"] for row in subset_rows]
        plt.scatter(xs, ys)

    plt.xlim([-0.01, 1.01])
    plt.ylim([-0.01, 1.01])
    plt.savefig(args.out_file, format=args.out_format)
    plt.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--breakout")
    parser.add_argument("--out-format", default="png")
    parser.add_argument("--subset", default="all")
    parser.add_argument("in_db")
    parser.add_argument("dataset")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
