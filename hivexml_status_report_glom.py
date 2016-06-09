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
Glom the three individual LaTeX report tables into one table.
"""

__version__ = "0.1.2"

import os
import logging

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    row_order = []
    datadict = dict()
    for (report_tex_no, report_tex) in enumerate(args.report_texs):
        dataset = report_tex.split("/")[1][5:]
        with open(report_tex, "r") as fh:
            for line in fh:
                cleaned_line = line.strip()
                if cleaned_line == "":
                    continue
                line_parts = cleaned_line[:-2].split(" & ")
                if report_tex_no == 0:
                    row_order.append(line_parts[0])
                datadict[(dataset, line_parts[0])] = line_parts[1]
    with open(args.output_tex, "w") as fh:
        fh.write(r" & Training & Evaluation & M57 \\")
        fh.write("\n")
        fh.write("\\midrule\n")
        for row_key in row_order:
            new_line = [row_key]
            for dataset in ["training", "evaluation", "m57"]:
                new_line.append( str(datadict[(dataset, row_key)]) )
            fh.write(" & ".join(new_line))
            fh.write(r"\\")
            fh.write("\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("output_tex")
    parser.add_argument("report_texs", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
