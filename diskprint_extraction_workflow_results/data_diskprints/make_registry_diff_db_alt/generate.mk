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
SEVENZIP ?= 7z
SHELL = /bin/bash

all: \
  deltas.db

deltas.db: \
  differ.cfg \
  differ_db_library.py \
  deltas_db.py \
  rx_make_database.py
	rm -f _deltas.db
	$(PYTHON3) deltas_db.py $(DEBUG_FLAG) _deltas.db
	mv _deltas.db deltas.db

deltas.db.zip: \
  deltas.db
	rm -f _$@
	$(SEVENZIP) -tzip a _$@ deltas.db
	mv _$@ $@

deltas.db.zip.sha512: \
  deltas.db.zip
	rm -f _$@
	openssl dgst -sha512 deltas.db.zip | awk '{print tolower($$(NF))}' > _$@
	mv _$@ $@

differ.cfg:
	@printf "\nPlease create a configuration file 'differ.cfg'.  A sample file 'differ.cfg.sample' shows the expected form.  (Only a database account with read permissions is necessary.)\n\n" >&2
	exit 72

dist: \
  deltas.db.zip \
  deltas.db.zip.sha512
