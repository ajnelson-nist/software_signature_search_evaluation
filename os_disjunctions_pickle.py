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
This is a reporting script that produces intermedate data for an HTML or LaTeX table describing the number of cells held in common by the baseline OS installations.
"""

__version__ = "0.3.2"

import os
import sys
import sqlite3
import collections
import logging
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer

def main():
    path_xp32_0 =  args.dwf_node_results_dir + "/234-1-234-1-150/format_registry_single_state.sh/registry_single_state.db"
    path_xp32_1 =  args.dwf_node_results_dir + "/11331-2-11331-2-90/format_registry_single_state.sh/registry_single_state.db"
    path_vista32 = args.dwf_node_results_dir + "/8504-1-8504-1-90/format_registry_single_state.sh/registry_single_state.db"
    path_vista64 = args.dwf_node_results_dir + "/8504-2-8504-2-90/format_registry_single_state.sh/registry_single_state.db"
    path_732 =     args.dwf_node_results_dir + "/9480-1-9480-1-150/format_registry_single_state.sh/registry_single_state.db"
    path_764 =     args.dwf_node_results_dir + "/9480-2-9480-2-150/format_registry_single_state.sh/registry_single_state.db"
    path_832 =     args.dwf_node_results_dir + "/14694-1-14694-1-60/format_registry_single_state.sh/registry_single_state.db"
    path_864 =     args.dwf_node_results_dir + "/14694-2-14694-2-50/format_registry_single_state.sh/registry_single_state.db"

    _logger.debug("Inspecting path: %r." % path_xp32_0)
    assert os.path.exists(path_xp32_0)
    assert os.path.exists(path_xp32_1)
    _logger.debug("Inspecting path: %r." % path_vista32)
    assert os.path.exists(path_vista32)
    assert os.path.exists(path_vista64)
    assert os.path.exists(path_732)
    assert os.path.exists(path_764)
    assert os.path.exists(path_832)
    assert os.path.exists(path_864)

    conns = collections.OrderedDict()
    conns["XP (1)"] = sqlite3.connect(path_xp32_0)
    conns["XP (2)"] = sqlite3.connect(path_xp32_1)
    conns["Vista-32"] = sqlite3.connect(path_vista32)
    conns["Vista-64"] = sqlite3.connect(path_vista64)
    conns["7-32"] = sqlite3.connect(path_732)
    conns["7-64"] = sqlite3.connect(path_764)
    conns["8-32"] = sqlite3.connect(path_832)
    conns["8-64"] = sqlite3.connect(path_864)

    cursors = dict()
    cellsets = dict()

    root_cell_metadata = []

    for osname in conns:
        logging.debug("Ingesting " + repr(osname) + ".")
        #conns[osname].isolation_level = "EXCLUSIVE"
        conns[osname].row_factory = sqlite3.Row
        cursors[osname] = conns[osname].cursor()
        cellsets[osname] = set()
        cursors[osname].execute("SELECT ca.cellname, ca.type, ha.filename FROM cell_analysis AS ca, hive_analysis AS ha WHERE ca.hive_id = ha.hive_id;")
        prefixes_nagged = set()
        for row in cursors[osname]:
            #Record the root cell paths for a normalizing aid report
            if row["type"] == "root":
                root_cell_metadata.append((osname, row["filename"], row["cellname"]))

            #Record the cell paths for overlap measurements
            if args.normalize:
                cellpath = normalizer.normalize_path(row["filename"], row["cellname"])

                #Record failures to normalize
                if cellpath == row["cellname"]:
                    prefix = normalizer.extract_prefix(cellpath)
                    if prefix not in prefixes_nagged:
                        prefixes_nagged.add(prefix)

                        logging.warning("This prefix failed to normalize: %r." % prefix)
                        logging.info("The image being ingested is: %r." % osname)
                        logging.info("It came from the hive at this path: %r." % row["filename"])
            else:
                cellpath = row["cellname"]
            cellsets[osname].add(cellpath)
        logging.debug("Ingested %d cell paths." % len(cellsets[osname]))

    win7_overlaps = set()
    thetable = dict()
    for osnamea in conns:
        for osnameb in conns:
            if osnamea == osnameb:
                thetally = len(cellsets[osnamea])
            else:
                the_overlaps = set.intersection(cellsets[osnamea], cellsets[osnameb])
                if set([osnamea,osnameb]) == set(["7-32","7-64"]):
                    win7_overlaps.update(the_overlaps)
                thetally = len(the_overlaps)
            thetable[(osnamea, osnameb)] = thetally
            thetable[(osnameb, osnamea)] = thetally

    _logger.debug("The table: %r." % thetable)

    osnames = [osname for osname in conns]

    with open(args.out_pickle, "wb") as out_fh:
        pickler = pickle.Pickler(out_fh)
        out_dict = {
          "osnames": osnames,
          "conns": {key:conns[key] for key in osnames},
          "thetable": thetable
        }
        pickler.dump(out_dict)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--root-metadata", action="store_true")
    parser.add_argument("dwf_node_results_dir")
    parser.add_argument("out_pickle")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()
