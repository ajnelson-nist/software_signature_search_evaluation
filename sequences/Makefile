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

DEBUG_FLAG ?=
PYTHON3 ?= python3.4

all: namedsequence.db

namedsequence.db: \
  differ_func_library.py \
  format_sequences.py \
  schema_namedsequence.sql
	rm -f _$@
	sqlite3 _$@ < schema_namedsequence.sql
	"$(PYTHON3)" format_sequences.py $(DEBUG_FLAG) _$@ m57 baselines preinstalled installclose repeated experiment1 idleappfork
	mv _$@ $@
