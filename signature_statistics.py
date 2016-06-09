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
Create, for each model, for each document, statistics about the document length.
"""

__version__ = "0.1.1"

import sqlite3

import TFIDFEngine

def main():
    #Load engine
    engine = TFIDFEngine.BasicTFIDFEngine()
    engine.load(args.vsm_pickle)

    conn = sqlite3.connect(args.out_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE doc_statistics (doc_name TEXT UNIQUE, doc_len INTEGER);")

    for doc_name in sorted(engine.corpus):
        doc_len = 0
        #Don't fail on empty signatures.
        if not doc_name in engine.tf:
            continue
        #Define length of document as number of terms that appear >0 times.
        for term in engine.tf[doc_name]:
            if engine.tf[doc_name].get(term, 0) > 0:
                doc_len += 1
        cursor.execute("INSERT INTO doc_statistics (doc_name, doc_len) VALUES (?,?);", (doc_name, doc_len))
    conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("vsm_pickle")
    parser.add_argument("out_db")
    args = parser.parse_args()

    main()
