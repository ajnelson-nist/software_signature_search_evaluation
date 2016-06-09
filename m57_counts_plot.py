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

#Script original source: I forgot to document from what example I started this plot, but it's likely this one:
#  <http://matplotlib.org/examples/api/date_demo.html>

from __future__ import print_function

__version__ = "0.2.1"

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import numpy as np
import matplotlib.pyplot as plt

import dfxml

#TODO Replace data structure in m57_meta
MACHINE_TIMES = {
  "charlie": {
    "charlie-2009-11-12start": "2009-11-12T08:00:00Z",
    "charlie-2009-11-12": "2009-11-12T16:00:00Z",
    "charlie-2009-11-16": "2009-11-16T16:00:00Z",
    "charlie-2009-11-17": "2009-11-17T16:00:00Z",
    "charlie-2009-11-18": "2009-11-18T16:00:00Z",
    "charlie-2009-11-19": "2009-11-19T16:00:00Z",
    "charlie-2009-11-20": "2009-11-20T16:00:00Z",
    "charlie-2009-11-23": "2009-11-23T16:00:00Z",
    "charlie-2009-11-24": "2009-11-24T16:00:00Z",
    "charlie-2009-11-30": "2009-11-30T16:00:00Z",
    "charlie-2009-12-01": "2009-12-01T16:00:00Z",
    "charlie-2009-12-02": "2009-12-02T16:00:00Z",
    "charlie-2009-12-03": "2009-12-03T16:00:00Z",
    "charlie-2009-12-04": "2009-12-04T16:00:00Z",
    "charlie-2009-12-07": "2009-12-07T16:00:00Z",
    "charlie-2009-12-08": "2009-12-08T16:00:00Z",
    "charlie-2009-12-09": "2009-12-09T16:00:00Z",
    "charlie-2009-12-10": "2009-12-10T16:00:00Z",
    "charlie-2009-12-11": "2009-12-11T14:00:00Z"
  },
  "jo-oldComputer": {
    "jo-2009-11-12start": "2009-11-12T08:00:00Z",
    "jo-2009-11-12": "2009-11-12T16:00:00Z",
    "jo-2009-11-16": "2009-11-16T16:00:00Z",
    "jo-2009-11-17": "2009-11-17T16:00:00Z",
    "jo-2009-11-18": "2009-11-18T16:00:00Z",
    "jo-2009-11-19": "2009-11-19T16:00:00Z",
    "jo-2009-11-20-oldComputer": "2009-11-20T12:00:00Z"
  },
  "jo-newComputer": {
    "jo-2009-11-20-newComputer": "2009-11-20T16:00:00Z",
    "jo-2009-11-23": "2009-11-23T16:00:00Z",
    "jo-2009-11-24": "2009-11-24T16:00:00Z",
    "jo-2009-11-30": "2009-11-30T16:00:00Z",
    "jo-2009-12-01": "2009-12-01T16:00:00Z",
    "jo-2009-12-02": "2009-12-02T16:00:00Z",
    "jo-2009-12-03": "2009-12-03T16:00:00Z",
    "jo-2009-12-04": "2009-12-04T16:00:00Z",
    "jo-2009-12-07": "2009-12-07T16:00:00Z",
    "jo-2009-12-08": "2009-12-08T16:00:00Z",
    "jo-2009-12-09": "2009-12-09T16:00:00Z",
    "jo-2009-12-10": "2009-12-10T16:00:00Z",
    "jo-2009-12-11-001": "2009-12-11T09:00:00Z",
    "jo-2009-12-11-002": "2009-12-11T14:00:00Z"
  },
  "pat": {
    "pat-2009-11-12start": "2009-11-12T08:00:00Z",
    "pat-2009-11-12": "2009-11-12T16:00:00Z",
    "pat-2009-11-16": "2009-11-16T16:00:00Z",
    "pat-2009-11-17": "2009-11-17T16:00:00Z",
    "pat-2009-11-18": "2009-11-18T16:00:00Z",
    "pat-2009-11-19": "2009-11-19T16:00:00Z",
    "pat-2009-11-20": "2009-11-20T16:00:00Z",
    "pat-2009-11-23": "2009-11-23T16:00:00Z",
    "pat-2009-11-24": "2009-11-24T16:00:00Z",
    "pat-2009-11-30": "2009-11-30T16:00:00Z",
    "pat-2009-12-01": "2009-12-01T16:00:00Z",
    "pat-2009-12-02": "2009-12-02T16:00:00Z",
    "pat-2009-12-03": "2009-12-03T16:00:00Z",
    "pat-2009-12-04": "2009-12-04T16:00:00Z",
    "pat-2009-12-07": "2009-12-07T16:00:00Z",
    "pat-2009-12-08": "2009-12-08T16:00:00Z",
    "pat-2009-12-09": "2009-12-09T16:00:00Z",
    "pat-2009-12-10": "2009-12-10T16:00:00Z",
    "pat-2009-12-11": "2009-12-11T14:00:00Z"
  },
  "terry-smallDrive": {
    "terry-2009-11-12start": "2009-11-12T08:00:00Z",
    "terry-2009-11-12": "2009-11-12T16:00:00Z",
    "terry-2009-11-16": "2009-11-16T16:00:00Z",
    "terry-2009-11-17": "2009-11-17T16:00:00Z",
    "terry-2009-11-18": "2009-11-18T16:00:00Z",
  },
  "terry-bigDrive": {
    "terry-2009-11-19": "2009-11-19T16:00:00Z",
    "terry-2009-11-20": "2009-11-20T16:00:00Z",
    "terry-2009-11-23": "2009-11-23T16:00:00Z",
    "terry-2009-11-24": "2009-11-24T16:00:00Z",
    "terry-2009-11-30": "2009-11-30T16:00:00Z",
    "terry-2009-12-01": "2009-12-01T16:00:00Z",
    "terry-2009-12-02": "2009-12-02T16:00:00Z",
    "terry-2009-12-03": "2009-12-03T16:00:00Z",
    "terry-2009-12-04": "2009-12-04T16:00:00Z",
    "terry-2009-12-07": "2009-12-07T16:00:00Z",
    "terry-2009-12-08": "2009-12-08T16:00:00Z",
    "terry-2009-12-09": "2009-12-09T16:00:00Z",
    "terry-2009-12-10": "2009-12-10T16:00:00Z",
    "terry-2009-12-11-001": "2009-12-11T09:00:00Z",
    "terry-2009-12-11-002": "2009-12-11T14:00:00Z"
  }
}

def machine_tag_timestamp(machine, tag):
    image_timestamp = dfxml.dftime(MACHINE_TIMES[machine][tag])
    image_datetime = image_timestamp.datetime()
    return image_datetime 

def main():
    fs_counts = dict()
    for (dirpath, dirnames, filenames) in os.walk(args.m57_results_root):
        for filename in filenames:
            if args.fs_or_reg == "fs":
                if filename != "filesystem.txt":
                    continue
            else:
                if filename != "registry.txt":
                    continue
            filepath = os.path.join(dirpath, filename)
            with open(filepath, "r") as fh:
                tally_str = fh.read(128)
                if len(tally_str) == 128 or not tally_str.isdigit():
                    raise ValueError("This path does not contain an ASCII-encoded numeric string: %r." % filepath)
                tally_int = int(tally_str)
                m57_tag = os.path.basename(dirpath)
                fs_counts[m57_tag] = tally_int
    _logger.debug("fs_counts = " + repr(fs_counts) + ".")
    if len(fs_counts) == 0:
        raise ValueError("Failed to load fs_counts data from this results root directory: %r." % args.m57_results_root)

    legend_sequence_list = []
    legend_subplot_list = []

    fig, ax = plt.subplots()
     
    #Make a line for each machine.
    for machine in sorted([machine for machine in MACHINE_TIMES.keys() ]):
        tags = [key for key in MACHINE_TIMES[machine]]

        plt.xlabel("Date of disk image")
        plt.ylabel("Allocated file count" if args.fs_or_reg == "fs" else "Allocated cell count")

        #Data as lists; converted to arrays after reading sequence tallies for each slice
        xsl = []
        ysl = []

        #Use a list of tuples so they can be sorted by timestamps
        pairs = []
        for (tag_no, tag) in enumerate(tags):
            if not tag in fs_counts.keys():
                continue
            image_datetime = machine_tag_timestamp(machine, tag)
            #_logger.debug("%r:\t%r" % (tag, image_timestamp))
            pairs.append((
              image_datetime,
              fs_counts[tag]
            ))
        for (ts, tally) in sorted(pairs):
            xsl.append(ts)
            ysl.append(tally)

        xsa = np.array(xsl)
        ysa = np.array(ysl)
        p = ax.plot(xsa, ysa, "-o")

        legend_sequence_list.append(machine)
        legend_subplot_list.append(p[0])

    ax.grid()

    plt.title("%s counts\nfor M57-Patents image sequences." % ("File system allocated-file" if args.fs_or_reg == "fs" else "Registry cell"))
    plt.xticks( rotation=90 )

    # Shink current axis by 20% to fit the legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0*2.5, box.width * 0.7, box.height*0.8])

    #plt.ylim(ymin=0)
    plt.legend( tuple(legend_subplot_list), tuple(legend_sequence_list), loc="center left", bbox_to_anchor=(1, 0.5))
    plt.savefig(args.output_pdf, format="pdf")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("m57_results_root")
    parser.add_argument("fs_or_reg", help="One of those two strings.")
    parser.add_argument("output_pdf")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.fs_or_reg not in ["fs", "reg"]:
        raise ValueError("fs_or_reg must be fs or reg.")

    main()
