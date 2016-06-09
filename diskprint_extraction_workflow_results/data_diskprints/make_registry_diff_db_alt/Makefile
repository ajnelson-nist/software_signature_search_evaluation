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
  inflate.done.log

.PHONY: \
  dist \
  download \
  generate

deltas.db:
	@printf "\nWithin this directory ($$PWD), either run 'make generate' to create deltas.db from the Diskprint Workflow results collected into Postgres; or run 'make download' to download a pre-created dataset.\n\n" >&2
	exit 72

dist:
	$(MAKE) -f generate.mk $@
	@printf "\ndeltas.db.zip and deltas.db.zip.sha512 are ready to upload.\n\n"

download:
	$(MAKE) -f download.mk

generate:
	$(MAKE) -f generate.mk

inflate.done.log: \
  deltas.db \
  differ_func_library.py \
  split.mk
	rm -rf by_edge
	$(MAKE) -f split.mk
	touch $@

split.mk: \
  namedsequence.db \
  split_mk.py
	rm -f _$@
	$(PYTHON3) split_mk.py $(DEBUG_FLAG) namedsequence.db _$@
	mv _$@ $@
