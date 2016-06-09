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

SEVENZIP ?= 7z

all: \
  inflate.done.log

.PHONY: \
  clean \
  download

clean:
	@rm -rf by_node inflate.done.log

download: \
  extraction_workflow_results_evaluation.zip.downloaded.log

extraction_workflow_results_evaluation.zip:
	wget http://www.nsrl.nist.gov/diskprint_data/evaluation/extraction_workflow_results_evaluation.zip.sha512
	wget -O _$@ http://www.nsrl.nist.gov/diskprint_data/evaluation/extraction_workflow_results_evaluation.zip
	test "x$$(openssl dgst -sha512 "_$@" | awk '{print tolower($$(NF))}')" == "x$$(cat $@.sha512)"
	mv _$@ $@

extraction_workflow_results_evaluation.zip.downloaded.log: \
  extraction_workflow_results_evaluation.zip
	touch $@

inflate.done.log: extraction_workflow_results_evaluation.zip.downloaded.log
	$(SEVENZIP) x extraction_workflow_results_evaluation.zip
	touch $@
