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
Create a database of hivexml exit states (for survival curves).
"""

__version__ = "0.10.1"

import sqlite3
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import Objects

import normalizer

#This function may error out.  That's ok.
def read_status_from_log(log_path):
    with open(log_path, "r") as fh:
        str_contents = fh.read(10).strip()
        int_contents = int(str_contents)
        if int_contents > 255:
            _logger.warning("Encountered unexpected data (int>255) in log %r." % log_path)
            return None
        return int_contents

def node_dir_id(node_dir_path, outcursor):
    outcursor.execute("SELECT rowid FROM machine_meta WHERE node_results_dir = ?;", (node_dir_path,))
    node_results_id = None
    for row in outcursor:
        node_results_id = row["rowid"]
    if node_results_id is None:
        raise ValueError("Insert or retrieval failed for node output dir: %r." % node_dir_path)
    return node_results_id

def out_db_conn_cursor(out_db_path):
    if os.path.exists(out_db_path):
        raise ValueError("Output db path must not already exist: %r." % out_db_path)
    outconn = sqlite3.connect(out_db_path)
    outconn.row_factory = sqlite3.Row
    outcursor = outconn.cursor()

    outcursor.execute("""\
CREATE TABLE machine_meta (
  node_results_dir TEXT,
  os_type TEXT,
  arch TEXT,
  hive_extraction_status INTEGER,
  PRIMARY KEY (node_results_dir)
);""")

    outcursor.execute("""\
CREATE TABLE hive_survival (
  node_results_id INTEGER NOT NULL,
  fiwalk_fileid INTEGER NOT NULL,
  filename TEXT NOT NULL,
  filesize_extracted INTEGER NOT NULL,
  filesize_from_fiwalk INTEGER NOT NULL,
  is_allocated BOOLEAN,
  extraction_exit_status INTEGER NOT NULL,
  sha1_extracted TEXT NOT NULL,
  sha1_from_fiwalk TEXT,
  hivexml_exit_status INTEGER,
  xmllint_exit_status INTEGER,
  hive_type TEXT NOT NULL
);""")

    outcursor.execute("""\
CREATE TABLE hives_failed_from_sqlite (
  node_results_id INTEGER,
  filename TEXT,
  cells_processed INTEGER,
  error_text TEXT,
  PRIMARY KEY (node_results_id, filename)
);""")

    outcursor.execute("""\
CREATE TABLE hive_analysis (
  node_results_id INTEGER,
  hive_id INTEGER,
  filename TEXT
);""")

    outcursor.execute("""\
CREATE TABLE hives_analyzed_in_sqlite (
  node_results_id INTEGER,
  hives_processed INTEGER,
  PRIMARY KEY (node_results_id)
);""")

    outcursor.execute("""\
CREATE TABLE cells_analyzed_in_sqlite (
  node_results_id INTEGER,
  cells_processed INTEGER,
  PRIMARY KEY (node_results_id)
);""")

    outconn.commit()

    return (outconn, outcursor)

def ingest_node_dir(node_dir_path, os_type, arch, outcursor):
    outcursor.execute("INSERT INTO machine_meta(node_results_dir, os_type, arch) VALUES (?,?,?);", (node_dir_path, os_type, arch))
    node_results_id = node_dir_id(node_dir_path, outcursor)

    rx_dir_path = os.path.join(node_dir_path, "invoke_regxml_extractor.sh")
    if not os.path.exists(rx_dir_path):
        raise ValueError("Could not find RegXML Extractor results directory: %r." % rx_dir_path)

    rss_dir_path = os.path.join(node_dir_path, "format_registry_single_state.sh")
    if not os.path.exists(rss_dir_path):
        raise ValueError("Could not find Registry single-state directory: %r." % rss_dir_path)

    extraction_status_log_path = os.path.join(rx_dir_path, "rx_extract_hives.py.status.log")
    extraction_status = read_status_from_log(extraction_status_log_path)
    outcursor.execute("UPDATE machine_meta SET hive_extraction_status = ? WHERE node_results_dir = ?;", (extraction_status, node_dir_path))

    rss_sqlite_path = os.path.join(rss_dir_path, "registry_single_state.db")
    rx_sqlite_path = os.path.join(rss_dir_path, "out.sqlite")
    if os.path.exists(rss_sqlite_path):
        _logger.debug("Ingesting database %r." % rss_sqlite_path)
        rss_sqlite_stat = os.stat(rss_sqlite_path)
        if rss_sqlite_stat.st_size > 0:
            outcursor.execute("ATTACH DATABASE '%s' AS rss;" % rss_sqlite_path)

            outcursor.execute("""\
INSERT INTO hives_analyzed_in_sqlite
  SELECT
    ?,
    COUNT(*)
  FROM
    rss.hive_analysis
;""", (node_results_id,))

            outcursor.execute("""\
INSERT INTO hive_analysis (node_results_id, hive_id, filename)
  SELECT
    ?,
    hive_id,
    filename
  FROM
    rss.hive_analysis
;""", (node_results_id,))

#TODO Parallelize...?  Replace 0 with COUNT(*) FROM rx.cell_analysis if ready to run a slow (20-minute) job.
#TODO Some of the Terry NTUSER.DAT files were re-allocated.  RegXML Extractor needs another reference field to disambiguate that hive from the rest of its ingest process.  It turns out that this count of cells analyzed is correct for now (the numbers agree with a previous calculation which I believe, not just think, was correct), but it should be updated in case future results make a mess.
            outcursor.execute("""\
INSERT INTO cells_analyzed_in_sqlite
  SELECT
    ?,
    COUNT(*)
  FROM
    rss.cell_analysis
;""", (node_results_id,))

        #NOTE Conditionally read reports of hive failures.  The condition is that sometimes the RegXML Extractor database turned up empty or non-existent (usually because of a blank OS disk state, for which RegXML Extractor 0.4.0 not-terribly-greatly doesn't create a SQLite database).
            if os.path.exists(rx_sqlite_path):
                rx_sqlite_stat = os.stat(rx_sqlite_path)
                if rx_sqlite_stat.st_size > 0:
                    outcursor.execute("ATTACH DATABASE '%s' AS rx;" % rx_sqlite_path)
                    outcursor.execute("""\
INSERT INTO hives_failed_from_sqlite
  SELECT
    ?,
    hive_file_path,
    cells_processed,
    error_text
  FROM
    rx.hives_failed AS hf,
    rss.hive_analysis AS ha
  WHERE
    hf.hive_id = ha.hive_id
;""", (node_results_id,))
                    outcursor.execute("DETACH DATABASE rx;")

            outcursor.execute("DETACH DATABASE rss;")

    extraction_manifest_path = os.path.join(rx_dir_path, "extraction.dfxml")

    for (event, obj) in Objects.iterparse(extraction_manifest_path):
        if not isinstance(obj, Objects.FileObject):
            continue

        fiwalk_fileid = obj.original_fileobject.id

        #Log whether the hive extraction succeeded or not.
        extraction_exit_status = 0
        if obj.error is None:
            extraction_exit_status = 0
        else:
            extraction_exit_status = 1

        filename = obj.original_fileobject.filename
        filesize_extracted = obj.filesize
        filesize_from_fiwalk = obj.original_fileobject.filesize
        sha1_extracted = obj.sha1
        sha1_from_fiwalk = obj.original_fileobject.sha1

        statuslog_path = os.path.join(rx_dir_path, "%d.hive.hivexml.status.log" % fiwalk_fileid)
        hivexml_exit_status = None
        with open(statuslog_path, "r") as fh:
            hivexml_exit_status = int(fh.read(8).strip())

        #Check xmllint status
        xmllint_exit_status = None
        xmllint_statuslog_basename = "%d.hive.xmllint.status.log" % fiwalk_fileid
        xmllint_statuslog_filepath = os.path.join(rx_dir_path, xmllint_statuslog_basename)
        if os.path.exists(xmllint_statuslog_filepath):
            with open(xmllint_statuslog_filepath, "r") as fh:
                xmllint_str = fh.read(100).strip()
                if xmllint_str == "":
                    raise ValueError("xmllint status log exists, but is blank: %r." % xmllint_statuslog_filepath)
                xmllint_exit_status = int(xmllint_str)

        hive_type = normalizer.hive_path_to_prefix(filename)

        results_tuple = (
          node_results_id,
          fiwalk_fileid,
          filename,
          filesize_extracted,
          filesize_from_fiwalk,
          obj.original_fileobject.is_allocated(),
          extraction_exit_status,
          sha1_extracted,
          sha1_from_fiwalk,
          hivexml_exit_status,
          xmllint_exit_status,
          hive_type
        )
        try:
            outcursor.execute("""\
INSERT INTO hive_survival (
  node_results_id,
  fiwalk_fileid,
  filename,
  filesize_extracted,
  filesize_from_fiwalk,
  is_allocated,
  extraction_exit_status,
  sha1_extracted,
  sha1_from_fiwalk,
  hivexml_exit_status,
  xmllint_exit_status,
  hive_type
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
;""", results_tuple)
        except:
            _logger.info(repr(extraction_manifest_path))
            _logger.info(repr(results_tuple))
            raise
