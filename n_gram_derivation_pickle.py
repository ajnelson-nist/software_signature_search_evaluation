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

import pickle
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))

import n_grammer

def main():
    _logger.debug("Loading cell parent map...")
    with open(args.cell_parent_pickle, "rb") as cp_fh:
        unpickler = pickle.Unpickler(cp_fh)
        n_grammer.parent_map = unpickler.load()
    _logger.debug("Done loading cell parent map.")

    #Key: Cell path.
    #Value: N-grams.
    outdict = dict()

    for cellpath in n_grammer.parent_map.keys():
        derived_terms = []

        if args.n_gram_length is None:
            #No n-gram request -> use whole term.
            derived_terms.append(cellpath)
        else:
            #Create all n-grams from term and parents.
            for n_gram in n_grammer.n_grams(cellpath, int(args.n_gram_length), args.last_n):
                derived_terms.append(n_gram)
        outdict[cellpath] = derived_terms

    with open(args.out_pickle, "wb") as out_fh:
        pickler = pickle.Pickler(out_fh)
        pickler.dump(outdict)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")

    parser.add_argument("--last-n", action="store_true", help="Only use last n components of path (n set by --n-gram-length).")
    parser.add_argument("--n-gram-length", type=int)
    parser.add_argument("cell_parent_pickle", help="Dictionary derived from cell_parent_db.py and dump_parent_map.py.")
    parser.add_argument("out_pickle")
    args = parser.parse_args()

    if args.last_n and args.n_gram_length is None:
        raise ValueError("--n-gram-length must be used if --last-n is used.")

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
