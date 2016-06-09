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

all: \
  all.done.log

.PHONY: clean

all.done.log: \
  plots.mk
	$(MAKE) -f plots.mk $@
	touch $@

clean:
	@rm all.done.log plots.mk
	@rm -rf stop_list_n_gram_strategy_*

plots.mk: \
  plots_mk.py
	rm -f _$@
	$(PYTHON3) plots_mk.py > _$@
	mv _$@ $@
