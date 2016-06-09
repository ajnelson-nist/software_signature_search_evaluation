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
Complete the ground truth table by augmenting ground truth positive to the left-complete set of ground truth.  (That is, left-of-beginning is marked as ground truth negative, right-of-end is unmarked, denoting unknown.)
"""

__version__ = "0.1.0"

import sqlite3
import os
import logging
import collections

_logger = logging.getLogger(os.path.basename(__file__))

import m57_meta

def main():
    doc_names = set()
    with sqlite3.connect(args.training_db) as trainingconn:
        trainingconn.row_factory = sqlite3.Row
        trainingcursor = trainingconn.cursor()
        trainingcursor.execute("SELECT DISTINCT doc_name FROM ground_truth_positive;")
        for row in trainingcursor:
            doc_names.add(row["doc_name"])

    inconn = sqlite3.connect(args.in_db)
    inconn.row_factory = sqlite3.Row
    incursor = inconn.cursor()

    outconn = sqlite3.connect(args.out_db)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    outcursor.execute("CREATE TABLE ground_truth(node_id STRING, doc_name STRING, present BOOLEAN);")

    node_ids = set()
    incursor.execute("SELECT DISTINCT node_id FROM ground_truth_positive;")
    for row in incursor:
        node_ids.add(row["node_id"])
    _logger.debug("node_ids: %r." % node_ids)

    _logger.debug("MACHINE_TAG_SEQUENCES: %r." % m57_meta.MACHINE_TAG_SEQUENCES)

    machine_tags = sorted(m57_meta.MACHINE_TAG_SEQUENCES.keys())
    _logger.debug("machine_tags: %r." % machine_tags)

    #Need table of ANY incidence of software within sequences.
    #Mentality:  Software presence within those sequences starts OFF, switches to ON in first ground truth hit, and switches to NULL on close of reported interval.  By design, no software recurs within a machines equence in the scenario.
    incursor.execute("SELECT DISTINCT node_id, doc_name FROM ground_truth_positive;")
    #Key: (machine_tag, doc_name)
    #Value: set of node_id index within sequence
    software_incidence = collections.defaultdict(set)
    for (row_no, row) in enumerate(incursor):
        node_id = row["node_id"]
        doc_name = row["doc_name"]
        for machine_tag in machine_tags:
            if node_id in m57_meta.MACHINE_TAG_SEQUENCES[machine_tag]:
                node_index = m57_meta.MACHINE_TAG_SEQUENCES[machine_tag].index(node_id)
                software_incidence[(machine_tag, doc_name)].add(node_index)
    _logger.debug("Rows read: %d." % row_no)

    _logger.debug("software_incidence: %r." % software_incidence)
    #Key: (machine_tag, doc_name)
    #Value: Pair, (int,int).  First int is the first Positive index, which may be the beginning of the sequence.  Second is the last Positive index, which may be the end of the sequence.
    ground_truth_intervals_boundaries = dict()

    ground_truth_positive_doc_names = set()
    ground_truth_positive_machine_tags = set()
    for (machine_tag, doc_name) in software_incidence:
        ground_truth_positive_machine_tags.add(machine_tag)
        ground_truth_positive_doc_names.add(doc_name)
        ground_truth_intervals_boundaries[(machine_tag, doc_name)] = (min(software_incidence[(machine_tag, doc_name)]), max(software_incidence[(machine_tag, doc_name)]))
    #Ensure no document names were invented.
    assert len(ground_truth_positive_doc_names - doc_names) == 0
    _logger.debug("ground_truth_intervals_boundaries: %r." % ground_truth_intervals_boundaries)

    for (machine_tag, doc_name) in ground_truth_intervals_boundaries:
        for index in range(len(m57_meta.MACHINE_TAG_SEQUENCES[machine_tag])):
            #Three states:  Absent, then Present, then Unknown.
            present = 0
            if index >= ground_truth_intervals_boundaries[(machine_tag, doc_name)][0]:
                present = 1
            if index > ground_truth_intervals_boundaries[(machine_tag, doc_name)][1]:
                present = None

            if present is None:
                continue

            node_id = m57_meta.MACHINE_TAG_SEQUENCES[machine_tag][index]
            outcursor.execute("INSERT INTO ground_truth VALUES (?,?,?);", (node_id, doc_name, present))
        
    outconn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("training_db")
    parser.add_argument("in_db")
    parser.add_argument("out_db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()

