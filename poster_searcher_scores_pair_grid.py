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

"""Make pair grid for 2015-05-13 poster."""

__version__ = "0.1.1"

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import searcher_scores_pair_grid

def main():
    searcher_scores_pair_grid.make_pair_grid(["sequences", "n_grams", "docs_by", "combinator"], ["f1"])

if __name__ == "__main__":
    args = searcher_scores_pair_grid.parser.parse_args()
    searcher_scores_pair_grid.args = args

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
