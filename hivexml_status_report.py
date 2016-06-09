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

__version__ = "0.5.2"

import sqlite3
import os
import logging
import collections

#Thousands separation <https://stackoverflow.com/a/1823101>
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    inconn = sqlite3.connect(args.input_db)
    inconn.row_factory = sqlite3.Row
    incursor = inconn.cursor()

    #Results dictionary under construction as a defaults dictionary
    ddrd = collections.defaultdict(lambda: 0)

    incursor.execute("SELECT COUNT(*) AS tally FROM machine_meta;")
    for row in incursor:
        ddrd["num_media_images"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival;")
    for row in incursor:
        ddrd["num_hives_found"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM machine_meta WHERE hive_extraction_status = 0;")
    for row in incursor:
        ddrd["num_successful_hive_extractions"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE extraction_exit_status = 0;")
    for row in incursor:
        ddrd["num_hives_extracted"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE filesize_extracted <> filesize_from_fiwalk;")
    for row in incursor:
        ddrd["num_hive_extractions_filesize_discrepancy"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE sha1_extracted <> sha1_from_fiwalk;")
    for row in incursor:
        ddrd["num_hive_extractions_sha1_discrepancy"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE sha1_from_fiwalk IS NULL;")
    for row in incursor:
        ddrd["num_hive_extractions_sha1_from_fiwalk_null"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE hivexml_exit_status = 0;")
    for row in incursor:
        ddrd["num_hivexml_succeeded"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE hivexml_exit_status <> 0;")
    for row in incursor:
        ddrd["num_hivexml_failed"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hive_survival WHERE hivexml_exit_status = 0 AND xmllint_exit_status <> 0;")
    for row in incursor:
        ddrd["num_xmllint_failed"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hives_failed_from_sqlite;")
    for row in incursor:
        ddrd["num_hivexml_dfxmlpy_failed"] = locale.format("%d", row["tally"], grouping=True)

    if ddrd["num_hivexml_dfxmlpy_failed"] == "0":
        ddrd["num_cells_dfxmlpy_aborted_processing"] = "0"
    else:
        incursor.execute("SELECT SUM(cells_processed) AS tally FROM hives_failed_from_sqlite;")
        for row in incursor:
            ddrd["num_cells_dfxmlpy_aborted_processing"] = locale.format("%d", row["tally"], grouping=True)

    incursor.execute("SELECT COUNT(*) AS tally FROM hives_analyzed_in_sqlite;")
    for row in incursor:
        ddrd["num_imgs_sqlite_ingested"] = locale.format("%d", row["tally"], grouping=True)
        
    incursor.execute("SELECT SUM(hives_processed) AS tally FROM hives_analyzed_in_sqlite;")
    for row in incursor:
        ddrd["num_hives_sqlite_ingested"] = locale.format("%d", row["tally"], grouping=True)
        
    incursor.execute("SELECT SUM(cells_processed) AS tally FROM cells_analyzed_in_sqlite;")
    for row in incursor:
        ddrd["num_cells_sqlite_ingested"] = locale.format("%d", row["tally"], grouping=True)
        
    out_fh = open(args.output_file, "w")
    if args.html:
      out_fh.write("""\
<table>
""")

      if args.caption:
          out_fh.write("""\
  <caption>%s</caption>
""" % args.caption)

      out_fh.write("""\
  <thead>
    <tr>
      <th>Description</th>
      <th>Tally</th>
    </tr>
  </thead>
  <tfoot></tfoot>
  <tbody>
    <tr>
      <th>Media images</th>
      <td>%(num_media_images)s</td>
    </tr>
    <tr>
      <th>Images with successful hive metadata extraction</th>
      <td>%(num_successful_hive_extractions)s</td>
    </tr>
    <tr>
      <th>Hives found</th>
      <td>%(num_hives_found)s</td>
    </tr>
    <tr>
      <th>Hives extracted with matching SHA-1</th>
      <td>%(num_hives_extracted)s</td>
    </tr>
    <tr>
      <th>Hives extracted with SHA-1 discrepancy</th>
      <td>%(num_hive_extractions_sha1_discrepancy)s</td>
    </tr>
    <tr>
      <th>Hives that hivexml could process</th>
      <td>%(num_hivexml_succeeded)s</td>
    </tr>
    <tr>
      <th>(-) Hives that hivexml could not process</th>
      <td>%(num_hivexml_failed)s</td>
    </tr>
    <tr>
      <td>(-) Hivexml files that xmllint could not process</td>
      <td>%(num_xmllint_failed)s</td>
    </tr>
    <tr>
      <td>(-) Hivexml files that dfxml.py could not process</td>
      <td>%(num_hivexml_dfxmlpy_failed)s</td>
    </tr>
    <tr>
      <td>(-) Cells discarded from dfxml.py failing</td>
      <td>%(num_cells_dfxmlpy_aborted_processing)s</td>
    </tr>
    <tr>
      <td>Total images in SQLite</td>
      <td>%(num_imgs_sqlite_ingested)s</td>
    </tr>
    <tr>
      <td>Total hives in SQLite</td>
      <td>%(num_hives_sqlite_ingested)s</td>
    </tr>
    <tr>
      <td>Total cells in SQLite</td>
      <td>%(num_cells_sqlite_ingested)s</td>
    </tr>
  </tbody>
</table>
""" % ddrd)
    elif args.tex:
      out_fh.write(r"""Media images & %(num_media_images)s \\
Images with successful hive metadata extraction & %(num_successful_hive_extractions)s \\
Hives found & %(num_hives_found)s \\
Hives extracted with matching SHA-1 & %(num_hives_extracted)s \\
(-) Hives extracted with SHA-1 discrepancy & %(num_hive_extractions_sha1_discrepancy)s \\
Hives that hivexml could process & %(num_hivexml_succeeded)s \\
(-) Hives that hivexml could not process & %(num_hivexml_failed)s \\
(-) Hivexml files that xmllint could not process & %(num_xmllint_failed)s \\
(-) Hivexml files that dfxml.py could not process & %(num_hivexml_dfxmlpy_failed)s \\
(-) Cells discarded from dfxml.py failing & %(num_cells_dfxmlpy_aborted_processing)s \\
Total images in end analysis & %(num_imgs_sqlite_ingested)s \\
Total hives in end analysis & %(num_hives_sqlite_ingested)s \\
Total cells in end analysis & %(num_cells_sqlite_ingested)s \\
""" % ddrd)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    outflags = parser.add_mutually_exclusive_group()
    outflags.add_argument("--html", action="store_true")
    outflags.add_argument("--tex", action="store_true")
    parser.add_argument("--debug", help="Turn on debug-level logging.", action="store_true")
    parser.add_argument("--caption", help="Only for HTML reports.")
    parser.add_argument("input_db")
    parser.add_argument("output_file")
    args = parser.parse_args()

    #Set up logging
    logging.basicConfig(
      format='%(asctime)s %(levelname)s: %(message)s',
      datefmt='%Y-%m-%dT%H:%M:%SZ',
      level=logging.DEBUG if args.debug else logging.INFO
    )

    main()
