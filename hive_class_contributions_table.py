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

__version__ = "0.2.0"

import os
import logging
import sqlite3
import sys

_logger = logging.getLogger(os.path.basename(__file__))

import normalizer

def main():
    conn = sqlite3.connect(args.hive_class_contributions_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    os_format = {
      "234-1": "XP/32",
      "8504-1": "V/32",
      "8504-2": "V/64",
      "9480-1": "7/32",
      "9480-2": "7/64",
      "11331-2": "XP/32",
      "14694-1": "8/32",
      "14694-2": "8/64"
    }
    os_order = [
      "XP/32",
      "V/32",
      "V/64",
      "7/32",
      "7/64",
      "8/32",
      "8/64"
    ]

    hive_class_format = {
      '__NORMROOT_USRCLASS_LOCALSERVICE__': "UsrClass (Loc. Svc.)",
      '__NORMROOT_USRCLASS_NETWORKSERVICE__': "UsrClass (Net. Svc.)",
      '__NORMROOT_NTUSER_CONFIG__': "NtUser (config)",
      '__NORMROOT_SECURITY_CONFIG__': "Security (config)",
      '__NORMROOT_SYSTEM_REPAIR__': "System (repair)",
      '__NORMROOT_NTUSER_REPAIR__': "NtUser (repair)",
      '__NORMROOT_SAM_REPAIR__': "Sam (repair)",
      '__NORMROOT_SECURITY_REPAIR__': "Security (repair)",
      '__NORMROOT_COMPONENTS_CONFIG__': "Components (config)",
      '__NORMROOT_SYSTEM_CONFIG__': "System (config)",
      '__NORMROOT_NTUSER_USER__': "NtUser (user)",
      '__NORMROOT_NTUSER_LOCALSERVICE__': "NtUser (Loc. Svc.)",
      '__NORMROOT_SOFTWARE_REPAIR__': "Software (repair)",
      '__NORMROOT_NTUSER_NETWORKSERVICE__': "NtUser (Net. Svc.)",
      '__NORMROOT_SAM_CONFIG__': "Sam (config)",
      '__NORMROOT_NTUSER_DEFAULT__': "NtUser (default)",
      '__NORMROOT_USRCLASS_USER__': "UsrClass (user)",
      '__NORMROOT_SOFTWARE_CONFIG__': "Software (config)"
    }
    hive_class_order = [
      "NtUser (user)",
      "NtUser (config)",
      "NtUser (default)",
      "NtUser (repair)",
      "NtUser (Loc. Svc.)",
      "NtUser (Net. Svc.)",

      "UsrClass (user)",
      "UsrClass (Loc. Svc.)",
      "UsrClass (Net. Svc.)",

      "Components (config)",

      "Security (config)",
      "Security (repair)",

      "System (config)",
      "System (repair)",

      "Sam (config)",
      "Sam (repair)",

      "Software (config)",
      "Software (repair)",
    ]
    s1 = set(normalizer.NORMALIZED_PREFIXES)
    s2 = set(hive_class_format.keys())
    if s1 != s2:
        _logger.info("Symmetric difference: %r." % (s1 ^ s2))
        raise ValueError("The set of labeled keys doesn't match the set of keys to label.")
    s3 = set(os_order)
    s4 = set(os_format.values())
    if s3 != s4:
        _logger.info("Symmetric difference: %r." % (s3 ^ s4))
        raise ValueError("The set of OS labels doesn't match the ordering set.")
    s5 = set(hive_class_order)
    s6 = set(hive_class_format.values())
    if s5 != s6:
        _logger.info("Symmetric difference: %r." % (s5 ^ s6))
        raise ValueError("The set of labeled keys doesn't match the set of keys to label.")

    #Prime table with all 0's, to reveal holes.
    matrix = dict()
    for hive_class in hive_class_format.values():
        matrix[hive_class] = dict()
        for os_label in os_format.values():
            matrix[hive_class][os_label] = 0

    cursor.execute("SELECT * FROM recs;")
    for row in cursor:
        os_label = os_format[row["osetid"]]
        hive_class = hive_class_format[row["hive_prefix"]]
        matrix[hive_class][os_label] += 1

    with open(args.out_file, "w") as fh:
        if args.html:
            fh.write("""\
<table>
  <thead>
    <tr>
      <th></th>
      <th>""")
            fh.write("</th><th>".join(os_order))
            fh.write("""</th>
    </tr>
  </thead>
  <tfoot></tfoot>
  <tbody>
""")
            for hive_class in hive_class_order:
                fh.write("""\
    <tr>
      <th>%s</th>
""" % hive_class)
                for os_label in os_order:
                    fh.write("""\
      <td>%d</td>
""" % matrix[hive_class][os_label])
                fh.write("""\
    </tr>
""")
            fh.write("""\
  </tbody>
</table>
""")
        elif args.latex:
            fh.write(" & ")
            fh.write(" & ".join(os_order))
            fh.write(" \\\\\n")
            for hive_class in hive_class_order:
                fh.write(hive_class)
                for os_label in os_order:
                    fh.write(" & %d" % matrix[hive_class][os_label])
                fh.write(" \\\\\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    format_group = parser.add_mutually_exclusive_group(required=True)
    format_group.add_argument("--html", action="store_true")
    format_group.add_argument("--latex", action="store_true")
    parser.add_argument("hive_class_contributions_db")
    parser.add_argument("out_file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()

