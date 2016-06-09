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
This program provides a TFIDF-based search engine.
"""

#In case this module takes on further inspection of vector space model parameters as enumerated by Zobel and Moffat [1998], the points in the code that would need tweaking are annotated with "[ZM98]" and a Q-expression string, wildcarded except for the variant parameter selection.

__version__ = "5.1.0"

import collections
import math
import logging
import os
import pickle

_logger = logging.getLogger(os.path.basename(__file__))

class BasicTFIDFEngine():
    """
    A class similar in spirit to https://github.com/gearmonkey/tfidf-python, but re-implemented for want of greatly mutating that class.
    """
    def __init__(self, *args, **kwargs):
        self.num_docs = 0

        """
        Document frequency.
        Key: Term.
        Value:  Number of documents in which the term appears.
        """
        self.df = dict()

        """
        Term frequency.
        Key:  Document
        Value: Dictionary; key: term; value: count of term within each document.
        """
        self.tf = dict()

        """
        Term-frequency, inverse-document-frequency matrix.
        Key: Document
        Value: Dictionary; key: term; value: tfidf of doc/term in corpus.
        """
        self.tfidf = dict()

        """
        Document names.
        """
        self.corpus = set()

    def ingest_document(self, doc_name, doc_terms):
        """
        The types of name and terms: String and List.

        The first time this function is called, the main dictionaies of this class are changed from vanilla dictionaries to defaultdicts, causing a potentially significant copy operation.
        """
        dictt = type(dict())

        #Promote dictionaries to writeables if this is the first document ingested.
        if type(self.df) == dictt:
            tmp = collections.defaultdict(lambda:0)
            for key in self.df.keys():
                tmp[key] = self.df[key]
            self.df = tmp

        if type(self.tf) == dictt:
            tmp = collections.defaultdict(lambda:collections.defaultdict(lambda:0))
            for key1 in self.tf.keys():
                for key2 in self.tf[key1].keys():
                    tmp[key1] = self.tf[key1][key2]
            self.tf = tmp

        if type(self.tfidf) == dictt:
            tmp = collections.defaultdict(lambda:collections.defaultdict(lambda:0.0))
            for key1 in self.tfidf.keys():
                for key2 in self.tfidf[key1].keys():
                    tmp[key1] = self.tfidf[key1][key2]
            self.tfidf = tmp

        #Assure types.
        assert isinstance(doc_name, str)
        assert isinstance(doc_terms, list)

        #Assure this is not a repeated ingest.
        assert doc_name not in self.corpus

        #Allow ingesting empty documents.
        #if len(doc_terms) == 0:
        #    _logger.info("Skipping ingesting document %r.  No terms presented." % doc_name)
        #    return

        #Update document frequency vector
        distinct_doc_terms = set(doc_terms)
        for term in distinct_doc_terms:
            self.df[term] += 1

        #Update term frequency matrix
        for term in doc_terms:
            self.tf[doc_name][term] += 1

        self.corpus.add(doc_name)
        self.num_docs += 1

        for doc in self.corpus:
            self.tfidf[doc] # Visibly a nop, but because self.tfidf is a defaultdict, this instantiates a defaultdict, making a record of doc in self.tfidf in case no terms appear.
            for term in self.df:
                #Only add an entry in tfidf[doc][term] if there is a non-0 term frequency.  This makes self.tfidf a sparse matrix, which the query function (particularly cos_sim) can handle.
                if self.tf[doc].get(term, 0) > 0:
                    #[ZM98] __-BB_-___
                    self.tfidf[doc][term] = self.tf[doc][term] * self.idf(term)

    def idf(self, term):
        """
        Add 1, per logarithmic formulation used in Zobel and Moffat, SIGIR '98, Table 2, formulation B.
        """
        #[ZM98] _B-___-___
        return math.log( 1 + float(self.num_docs)/self.df[term], 2 )

    def query(self, query_terms):
        """
        Returns a list of pairs, cosine similarity to @query_terms and the document ID.

        The argument to this function is *Query terms*, not *Registry paths.*  The document ingest and query preparation functions outside of the Engine should have handled the logistics of transformation and stop listing.
        """
        assert isinstance(query_terms, list)

        retval = []

        #Check that the query can be run
        if len(query_terms) == 0:
            _logger.info("No searchable terms presented in query.")
            return retval

        #Build query term frequency. 
        q_tf = collections.Counter(query_terms)

        #Build set of overlapping terms.  (This agrees with Zobel and Moffat's "Standard formulation.")
        terms_in_common = set.intersection( set(q_tf.keys()), set(self.df.keys()) )

        #Check again that the query can be run
        if len(terms_in_common) == 0:
            _logger.info("No query terms in common with search engine.")
            return retval

        #Build query tfidf vector.
        q_tfidf = collections.defaultdict(lambda:0.0)
        for term in terms_in_common:
            #This definition is consistent with Zobel and Moffat's "Standard formulation," using raw counts for the relative (weighted) term frequency of a term t within the query q.
            #[ZM98] __-___-BB_
            q_tfidf[term] = q_tf[term] * self.idf(term)

        #Rank documents by cosine similarity, term frequency-inverse document frequency weights
        for doc in self.corpus:
            #Skip empty documents; cosine is undefined for 0-length documents.
            if len(self.tf[doc]) == 0:
                continue

            try:
                doc_cos_sim = cos_sim(q_tfidf, self.tfidf[doc])
                retval.append((doc_cos_sim, doc))
            except:
                _logger.error("Error encountered computing cosine similarity.")
                _logger.error("Document: %r." % doc)
                _logger.error("Document term tally: %r." % len(self.tf[doc]))
                _logger.error("Query term tally (in common with search engine): %r." % len(terms_in_common))
                _logger.error("Document vector length: %r." % doc_length(self.tfidf[doc]))
                _logger.error("Query vector length: %r." % doc_length(q_tfidf))
                raise

        return retval

    def check_self(self):
        min_doc_length = float("inf")
        min_doc_length_name = None
        for doc in self.corpus:
            dl = doc_length(self.tfidf[doc])
            if dl < min_doc_length:
                min_doc_length = dl
                min_doc_length_name = doc
            if dl == 0:
                _logger.warning("0-length document: %r." % doc)
                _logger.warning("Top three document tfidf magnitudes: %r." % sorted(self.tfidf[doc].values(), reverse=True)[:3])
                _logger.warning("Top three document tf magnitudes: %r." % sorted(self.tf[doc].values(), reverse=True)[:3])
        _logger.debug("Minimum document length: %r, for %r." % (min_doc_length, min_doc_length_name))

    def populate_from_picklable(self, pobj):
        """Populates the class data structures with an object produced by to_picklable."""
        for prop in ["num_docs", "corpus", "df", "tf", "tfidf"]:
            setattr(self, prop, pobj[prop])

    def load(self, filepath):
        with open(filepath, "rb") as fh:
            unpickler = pickle.Unpickler(fh)
            pobj = unpickler.load()
            self.populate_from_picklable(pobj)

    def to_picklable(self):
        """Returns an object that can be written to a pickle file."""
        dictt = type(dict())

        pobj = dict()
        #Copy simpler objects.
        for prop in ["num_docs", "corpus"]:
            pobj[prop] = getattr(self, prop)

        #Convert defaultdicts to regular dictionaries.  (Functions can't be pickled.)
        if type(self.df) == dictt:
            pobj["df"] = self.df
        else:
            _logger.debug("Simplifying df...")
            pdf = dict()
            for key in self.df.keys():
                pdf[key] = self.df[key]
            pobj["df"] = pdf
            _logger.debug("Done.")

        if type(self.tf) == dictt:
            pobj["tf"] = self.tf
        else:
            _logger.debug("Simplifying tf...")
            ptf = dict()
            for key1 in self.tf.keys():
                ptf[key1] = dict()
                for key2 in self.tf[key1].keys():
                    ptf[key1][key2] = self.tf[key1][key2]
            pobj["tf"] = ptf
            _logger.debug("Done.")

        if type(self.tfidf) == dictt:
            pobj["tfidf"] = self.tfidf
        else:
            _logger.debug("Simplifying tfidf...")
            ptfidf = dict()
            for key1 in self.tfidf.keys():
                ptfidf[key1] = dict()
                for key2 in self.tfidf[key1].keys():
                    ptfidf[key1][key2] = self.tfidf[key1][key2]
            pobj["tfidf"] = ptfidf
            _logger.debug("Done.")

        return pobj

    def save(self, filepath):
        """Persist with pickle."""
        with open(filepath, "wb") as fh:
            pickler = pickle.Pickler(fh, protocol=3)
            pobj = self.to_picklable()
            _logger.debug("Writing to pickle file...")
            pickler.dump(pobj)
            _logger.debug("Done.")

    def stats(self):
        print("Number of documents: %d." % self.num_docs)
        print("Number of terms: %d." % len(self.df))

def doc_length(doc_vector):
    #_logger.debug("doc_length: Called on:\n\t%s" % doc_vector)
    #[ZM98] __-__B-__B
    #NOTE: Query length is based on the terms in the intersection of the sets of terms from the query, with the union of terms from all documents.  Truncating the query has an effect on its effective length in the calculations, but is in fairness to IDF calculations that would have to divide by 0 if the query terms not present in the engine were included in the ultimately-executed query.
    the_sum = 0.0
    for term in doc_vector:
        the_sum += doc_vector[term]**2
    return math.sqrt(the_sum)

def cos_sim(v1, v2):
    #[ZM98] B_-___-___
    return dot(v1,v2) / (doc_length(v1) * doc_length(v2))

def dot(v1, v2):
    mutual_terms = set(v1.keys()).union(set(v2.keys()))
    running_sum = 0.0
    for term in mutual_terms:
        running_sum += v1.get(term, 0.0) * v2.get(term, 0.0)
    return running_sum
