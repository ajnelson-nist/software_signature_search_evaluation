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

import pickle

import SignatureSearcher

def main():
    searcher = SignatureSearcher.SignatureSearcher()
    searcher.load(args.signature_searcher_pickle)
    with open(args.output_pickle, "wb") as fh:
        pickler = pickle.Pickler(fh)
        pickler.dump(searcher.doc_threshold)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("signature_searcher_pickle")
    parser.add_argument("output_pickle")
    args = parser.parse_args()

    main()
