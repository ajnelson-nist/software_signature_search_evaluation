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

__version__ = "0.5.0"

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import NullFormatter

def main():
    conn = sqlite3.connect(args.in_db)
    conn.row_factory = sqlite3.Row

    if args.subset == "all":
        sql = "SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%s';" % args.dataset
    elif args.subset == "nocontrol":
        sql = "SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = '%s' AND sequences <> 'experiment1';" % args.dataset
    else:
        raise NotImplementedError("Subset argument not implemented: %r." % args.subset)
    _logger.debug("sql = %r." % sql)
    df = pd.io.sql.read_sql(sql, conn)

    if args.axes_pair == "precrec":
        x = df["recall"]
        y = df["precision"]
    elif args.axes_pair == "f1num":
        x = df["nonzerolen_doc_count"]
        y = df["f1"]
    elif args.axes_pair == "f1nratio":
        x = df["proportion_nonzerolen"]
        y = df["f1"]
    elif args.axes_pair == "precnum":
        x = df["nonzerolen_doc_count"]
        y = df["precision"]
    elif args.axes_pair == "precnratio":
        x = df["proportion_nonzerolen"]
        y = df["precision"]
    elif args.axes_pair == "recnum":
        x = df["nonzerolen_doc_count"]
        y = df["recall"]
    elif args.axes_pair == "recnratio":
        x = df["proportion_nonzerolen"]
        y = df["recall"]
    else:
        raise NotImplementedError("Axes pair request not implemented: %r." % args.axes_pair)

    nullfmt = NullFormatter()         # no labels
    
    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02
    
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]
    
    # start with a rectangular Figure
    plt.figure(1, figsize=(8, 8))
    
    axScatter = plt.axes(rect_scatter)

    if args.axes_pair == "precrec":
        plt.xlabel("Recall")
        plt.ylabel("Precision")
    elif args.axes_pair == "f1num":
        plt.xlabel("Count of nonzero documents")
        plt.ylabel("F1")
    elif args.axes_pair == "f1nratio":
        plt.xlabel("Proportion of nonzero documents")
        plt.ylabel("F1")
    elif args.axes_pair == "precnum":
        plt.xlabel("Count of nonzero documents")
        plt.ylabel("Precision")
    elif args.axes_pair == "precnratio":
        plt.xlabel("Proportion of nonzero documents")
        plt.ylabel("Precision")
    elif args.axes_pair == "recnum":
        plt.xlabel("Count of nonzero documents")
        plt.ylabel("Recall")
    elif args.axes_pair == "recnratio":
        plt.xlabel("Proportion of nonzero documents")
        plt.ylabel("Recall")
    else:
        raise NotImplementedError("Axes label not implemented for pair request: %r." % args.axes_pair)

    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)
    
    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)
    
    # the scatter plot:
    axScatter.scatter(x, y)
    
    # now determine nice limits by hand:
    binwidth = 0.1
    xymax = np.max([np.max(np.fabs(x)), np.max(np.fabs(y))])
    _logger.debug("xymax = %r." % xymax)
    lim = (int(xymax/binwidth) + 1) * binwidth
    _logger.debug("lim = %r." % lim)
    
    if args.axes_pair in ["f1num", "precnum", "recnum"]:
        axScatter.set_xlim((0, lim*1.1))
    else:
        axScatter.set_xlim((-0.1, 1.1))
    axScatter.set_ylim((-0.1, 1.1))
    
    xbinwidth = binwidth * xymax
    xbins = np.arange(-lim, lim + binwidth, xbinwidth)
    _logger.debug("xbins = %r." % xbins)
    axHistx.hist(x, bins=xbins)

    ybins = np.arange(-0.1, 1.1 + binwidth, binwidth)
    _logger.debug("ybins = %r." % ybins)
    axHisty.hist(y, bins=ybins, orientation='horizontal')
    
    #Key axis adjustment hint c/o:
    #  https://stackoverflow.com/a/12110715
    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())
    plt.xticks(rotation='vertical')

    plt.savefig(args.out_file, format="pdf")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--subset", choices={"all", "nocontrol"})
    parser.add_argument("in_db")
    parser.add_argument("dataset")
    parser.add_argument("axes_pair")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
