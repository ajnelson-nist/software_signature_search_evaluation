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

"""Make pair grid for presentation."""

__version__ = "0.2.0"

import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import searcher_scores_pair_grid

def main():
    if args.grid_size == "1x4":
        xs = ["sequences", "n_grams", "docs_by", "combinator"]
        ys = ["f1"]
    elif args.grid_size == "2x5":
        xs = ["sequences", "n_grams", "stop_list", "stop_list_n_gram_strategy", "docs_by"]
        ys = ["precision","recall"]
    elif args.grid_size == "3x4":
        xs = ["sequences", "n_grams", "docs_by", "combinator"]
        ys = ["precision","recall","f1"]
    else:
        raise NotImplementedError("--grid-size parameter %r is not implemented." % parser.grid_size)
    searcher_scores_pair_grid.make_pair_grid(xs, ys)

if __name__ == "__main__":
    parser = searcher_scores_pair_grid.parser
    parser.add_argument("--grid-size", choices={"1x4", "2x5", "3x4"})
    args = parser.parse_args()
    searcher_scores_pair_grid.args = args

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
