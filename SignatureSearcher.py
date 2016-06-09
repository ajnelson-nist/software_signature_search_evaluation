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

import TFIDFEngine

class SignatureSearcher(object):

    def __init__(self, vsm=None):
        self._doc_threshold = dict()

        if vsm is None:
            self._vsm = TFIDFEngine.BasicTFIDFEngine()
        else:
            self._vsm = vsm

    #I/O
    def load(self, filepath):
        with open(filepath, "rb") as fh:
            unpickler = pickle.Unpickler(fh)
            (doc_threshold, vsm) = unpickler.load()
            self.vsm.populate_from_picklable(vsm)
            self._doc_threshold = doc_threshold

    #I/O
    def save(self, filepath):
        ovsm = self.vsm.to_picklable()
        with open(filepath, "wb") as fh:
            pickler = pickle.Pickler(fh, protocol=3)
            pickler.dump((self._doc_threshold, ovsm))

    def query(self, terms):
        results = self.vsm.query(terms)
        hits = []
        for (score, doc_name) in results:
            if doc_name in self.doc_threshold:
                if score >= self.doc_threshold[doc_name]:
                    hits.append((score, doc_name))
        return hits

    @property
    def doc_threshold(self):
        """
        Dictionary of document threshold values.  That is, if a search score for a query is above the threshold value, that is considered a 'hit' for that document.
        Key: Document name.
        Value: Float.

        There is intentionally no setter for this property.
        """
        return self._doc_threshold

    @property
    def vsm(self):
        """
        Vector Space Model object -- a BasicTFIDFEngine.

        There is intentionally no setter for this property.
        """
        return self._vsm
