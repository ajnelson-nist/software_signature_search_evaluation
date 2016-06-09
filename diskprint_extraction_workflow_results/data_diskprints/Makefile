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
SEVENZIP ?= 7z
SHELL = /bin/bash

all: \
  inflate.done.log

.PHONY: \
  alt \
  clean \
  download

alt: \
  inflate.alt.done.log

#This target removes the flag files indicating the inflate completed, but not the zip files.  This is in case extraction is to be run again.
clean:
	@rm -rf by_edge by_node inflate.done.log */inflate.done.log
	@rm -r format_registry_single_state/by_node
	@rm -r invoke_regxml_extractor/by_node
	@rm -r make_registry_diff_db/by_edge
	@rm -f */all_dirs.txt
	@rm -f */all_files.txt

download: \
  inflate.done.log

format_registry_single_state/all_dirs.txt: \
  format_registry_single_state/inflate.done.log
	rm -f $$(dirname $@)/_$$(basename $@)
	cd format_registry_single_state ; find by_node -type d | sort > _$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

format_registry_single_state/all_files.txt: \
  format_registry_single_state/inflate.done.log
	rm -f $$(dirname $@)/_$$(basename $@)
	cd format_registry_single_state ; find by_node -type f | sort > _$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

format_registry_single_state/inflate.done.log:
	$(MAKE) -C format_registry_single_state inflate.done.log

#This recipe mirrors inflate.done.log's, except it uses the alternate derivation of Registry differences (rdifference).
inflate.alt.done.log: \
  format_registry_single_state/all_dirs.txt \
  format_registry_single_state/all_files.txt \
  invoke_regxml_extractor/all_dirs.txt \
  invoke_regxml_extractor/all_files.txt \
  make_registry_diff_db/all_dirs.txt \
  make_registry_diff_db_alt/inflate.done.log
	cat format_registry_single_state/all_dirs.txt | xargs mkdir -p
	rsync -av --progress --files-from=format_registry_single_state/all_files.txt format_registry_single_state/ ./
	cat invoke_regxml_extractor/all_dirs.txt | xargs mkdir -p
	rsync -av --progress --files-from=invoke_regxml_extractor/all_files.txt invoke_regxml_extractor/ ./
	rm -rf by_edge #Remove any downloaded edges from normal Registry difference derivation (set subtraction)
	cat make_registry_diff_db/all_dirs.txt | xargs mkdir -p
	rsync -av --progress make_registry_diff_db_alt/by_edge/ by_edge/
	@printf "\nAlternate copying completed.\n"
	touch inflate.done.log #NOTE: Pretend regular inflate process finished.
	touch inflate.alt.done.log

#For each downloaded zip:
#  First, the recipe creates all of the directories extracted from the zips.
#  Then, it copies each file from the extracted-zip directory into the directory structure that is similar to the diskprint workflow extraction results (as though they are freshly-generated).
inflate.done.log: \
  format_registry_single_state/all_dirs.txt \
  format_registry_single_state/all_files.txt \
  invoke_regxml_extractor/all_dirs.txt \
  invoke_regxml_extractor/all_files.txt \
  make_registry_diff_db/all_dirs.txt \
  make_registry_diff_db/all_files.txt
	cat format_registry_single_state/all_dirs.txt | xargs mkdir -p
	rsync -av --progress --files-from=format_registry_single_state/all_files.txt format_registry_single_state/ ./
	cat invoke_regxml_extractor/all_dirs.txt | xargs mkdir -p
	rsync -av --progress --files-from=invoke_regxml_extractor/all_files.txt invoke_regxml_extractor/ ./
	cat make_registry_diff_db/all_dirs.txt | xargs mkdir -p
	rsync -av --progress --files-from=make_registry_diff_db/all_files.txt make_registry_diff_db/ ./
	@printf "\nCopying completed.  You may want to run 'make clean' now to remove the originally-copied files.  The various 'all.zip' files will remain.\n"
	touch $@

invoke_regxml_extractor/all_dirs.txt: \
  invoke_regxml_extractor/inflate.done.log
	rm -f $$(dirname $@)/_$$(basename $@)
	cd invoke_regxml_extractor ; find by_node -type d | sort > _$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

invoke_regxml_extractor/all_files.txt: \
  invoke_regxml_extractor/inflate.done.log
	rm -f $$(dirname $@)/_$$(basename $@)
	cd invoke_regxml_extractor ; find by_node -type f | sort > _$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

invoke_regxml_extractor/inflate.done.log:
	$(MAKE) -C invoke_regxml_extractor inflate.done.log

make_registry_diff_db/all_dirs.txt: \
  make_registry_diff_db/inflate.done.log
	rm -f $$(dirname $@)/_$$(basename $@)
	cd make_registry_diff_db ; find by_edge -type d | sort > _$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

make_registry_diff_db/all_files.txt: \
  make_registry_diff_db/inflate.done.log
	rm -f $$(dirname $@)/_$$(basename $@)
	cd make_registry_diff_db ; find by_edge -type f | sort > _$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

make_registry_diff_db/inflate.done.log:
	$(MAKE) -C make_registry_diff_db inflate.done.log

make_registry_diff_db_alt/inflate.done.log:
	$(MAKE) -C make_registry_diff_db_alt inflate.done.log
