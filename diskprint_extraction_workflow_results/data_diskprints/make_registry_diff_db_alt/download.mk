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
  deltas.db.zip \
  deltas.db.zip.sha512

deltas.db: \
  deltas.db.zip
	$(SEVENZIP) x deltas.db.zip

deltas.db.zip: \
  deltas.db.zip.sha512
	rm -f _$@
	wget -O _$@ http://www.nsrl.nist.gov/diskprint_data/diskprints/by_script/make_registry_diff_db_alt/$@
	test "x$$(openssl dgst -sha512 _$@ | awk '{print tolower($$(NF))}')" == "x$$(cat $@.sha512)"
	mv _$@ $@

deltas.db.zip.sha512:
	rm -f _$@
	wget -O _$@ http://www.nsrl.nist.gov/diskprint_data/diskprints/by_script/make_registry_diff_db_alt/$@
	mv _$@ $@
