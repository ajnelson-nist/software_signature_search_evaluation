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
This script runs a basic sanity-check calculation.

Using example exercise from:
http://www.site.uottawa.ca/~diana/csi4107/cosine_tf_idf_example.pdf
"""

import unittest
import os
import logging
import math

_logger = logging.getLogger(os.path.basename(__file__))

import TFIDFEngine

class TestTFIDFComputations(unittest.TestCase):
    def setUp(self):
        self.engine = TFIDFEngine.BasicTFIDFEngine()

        self.corpus = dict()
        self.corpus["d1"] = ["new", "york", "times"]
        self.corpus["d2"] = ["new", "york", "post"]
        self.corpus["d3"] = ["los", "angeles", "times"]

        for doc in self.corpus:
            self.engine.ingest_document(doc, self.corpus[doc])

    def test_absent_query_term(self):
        "Run a query for new terms, seeing that the engine doesn't crash."
        self.engine.query(["not_in_corpus"])

    def test_tfidf(self):
        "Spot-check a few weight equalities."
        _logger.debug(self.engine.tfidf)
        self.assertEqual(self.engine.tfidf["d3"]["los"], self.engine.tfidf["d3"]["angeles"] )
        self.assertEqual(self.engine.tfidf["d1"]["new"], self.engine.tfidf["d2"]["york"] )
        self.assertEqual(self.engine.tfidf["d1"]["times"], self.engine.tfidf["d3"]["times"] )

    def test_results(self):
        query = ["new", "new", "times"]
        results = self.engine.query(query)
        _logger.debug("results = %r." % results)
        expected_order = ["d1", "d2", "d3"]
        results_order = [ r[1] for r in sorted(results, reverse=True) ]
        self.assertEqual(results_order, expected_order)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
