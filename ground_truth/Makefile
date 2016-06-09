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
  ground_truth.mk.done.log

.PHONY: check dist

check: \
  ground_truth.mk.done.log
	$(MAKE) -f ground_truth.mk $@

dist: \
  ../etid_to_productname.db \
  first_appearance_evaluation_image.py \
  ground_truth.mk.done.log \
  tablify_evaluation_ground_truth.py
	$(MAKE) -f ground_truth.mk $@

ground_truth.mk: \
  ground_truth_mk.py
	rm -f _$@
	$(PYTHON3) ground_truth_mk.py $(DEBUG_FLAG) _$@
	mv _$@ $@

ground_truth.mk.done.log: \
  ../differ_func_library.py \
  ../experiments/m57_roussev_dfrws12/application_appearances.py \
  ../experiments/m57_roussev_dfrws12/db.py \
  ../sequences/namedsequence.db \
  ../m57_meta.py \
  cartesian_ground_truth_completion.py \
  check_ground_truth_negative_m57.sh \
  check_ground_truth_positive_doc_names.sh \
  check_ground_truth_uniqueness.sh \
  check_versions_counts_consistent.sh \
  ground_truth.mk \
  ground_truth_evaluation_image_app.sql \
  ground_truth_evaluation_image_osapp.sql \
  ground_truth_grouped.py \
  m57_ground_truth_completion.py \
  ground_truth.py
	$(MAKE) -f ground_truth.mk
	touch $@
