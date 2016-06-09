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

__version__ = "0.1.0"

import logging
import os

#Thousands separation <https://stackoverflow.com/a/1823101>
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

_logger = logging.getLogger(os.path.basename(__file__))

def main():
    with open(args.in_tex, "r") as in_fh:
        for line in in_fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            line_parts = cleaned_line.split(" & ")
            tally = int(line_parts[0])
            formatted_tally = locale.format("%d", tally, grouping=True)
            print("%s & %s" % (formatted_tally, line_parts[1]))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("in_tex")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
