#!/usr/bin/make -f

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

PYTHON2 ?= python2.7
PYTHON3 ?= python3.4

all: \
  check

.PHONY: \
  check \
  check-n-gram-construction \
  check-sqlite \
  check-tfidf_computations

check: \
  check-n-gram-construction \
  check-sqlite \
  check-tfidf_computations

check-n-gram-construction: \
  n_gram_construction.py \
  n_grammer.py
	$(PYTHON3) n_gram_construction.py

check-sqlite: \
  sqlite_cursors.py \
  sqlite_cursors_tmp1.db \
  sqlite_cursors_tmp2.db
	rm -f sqlite_cursors_tmp3.db && $(PYTHON3) sqlite_cursors.py

check-tfidf_computations: \
  TFIDFEngine.py \
  tfidf_computations.py
	$(PYTHON3) tfidf_computations.py

sqlite_cursors_tmp1.db:
	rm -f _$@
	sqlite3 _$@ 'CREATE TABLE foo(x INTEGER); INSERT INTO foo VALUES (1); SELECT * FROM foo;'
	mv _$@ $@

sqlite_cursors_tmp2.db:
	rm -f _$@
	sqlite3 _$@ 'CREATE TABLE bar(y NUMBER); INSERT INTO bar VALUES (2.5); SELECT * FROM bar;'
	mv _$@ $@
