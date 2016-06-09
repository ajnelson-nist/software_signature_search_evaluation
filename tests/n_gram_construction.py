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
Test construction of n grams from Registry paths.
"""

import unittest

import n_grammer

class TestNGramConstruction(unittest.TestCase):
    def setUp(self):
        self.path_1comp = r"\foo"
        self.path_2comp = r"\foo\bar"
        self.path_3comp = r"\foo\bar\baz"

        n_grammer.parent_map[self.path_3comp] = (self.path_2comp, "baz")
        n_grammer.parent_map[self.path_2comp] = (self.path_1comp, "bar")
        n_grammer.parent_map[self.path_1comp] = (None, "foo")

    def test_unigrams(self):
        bigrams = [n_gram for n_gram in n_grammer.n_grams(self.path_3comp, 1)]
        self.assertEqual(bigrams, [r"baz", r"bar", r"foo"])

    def test_bigrams(self):
        bigrams = [n_gram for n_gram in n_grammer.n_grams(self.path_3comp, 2)]
        self.assertEqual(bigrams, [r"bar\baz", r"foo\bar"])

    def test_trigrams(self):
        bigrams = [n_gram for n_gram in n_grammer.n_grams(self.path_3comp, 3)]
        self.assertEqual(bigrams, [r"foo\bar\baz"])

    def test_last_bigrams(self):
        bigrams = [n_gram for n_gram in n_grammer.n_grams(self.path_3comp, 2, True)]
        self.assertEqual(bigrams, [r"bar\baz"])

    #def test_basename_chain_printing(self):
    #    for basename in n_grammer.basename_chain(self.path_3comp):
    #        print(basename)

    #def test_n_grams_printing(self):
    #    for n_gram in n_grammer.n_grams(self.path_3comp, 2):
    #        print(n_gram)

if __name__ == "__main__":
    unittest.main()
