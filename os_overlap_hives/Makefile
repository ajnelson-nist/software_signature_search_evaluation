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

PYTHON3 ?= python3.4

all: \
  732_vs_764.html \
  832_vs_864.html \
  latex_832_vs_864.tex \
  vista32_vs_vista64.html \
  vista32_vs_832.html \
  vista32_vs_864.html \
  vista64_vs_832.html \
  vista64_vs_864.html \
  xp320_vs_xp321.html

clean:
	@rm *html *tex

DISKPRINT_RESULTS.linked.log: \
  ../diskprint_extraction_workflow_results/data_diskprints/inflate.done.log
	rm -f DISKPRINT_RESULTS ; ln -s "$$PWD/../diskprint_extraction_workflow_results/data_diskprints" DISKPRINT_RESULTS
	touch $@

%.html: \
  %.sql \
  _header_html.sql \
  _header_files.sql \
  DISKPRINT_RESULTS.linked.log
	rm -f _$@
	echo "<TABLE BORDER='1'>" > _$@
	sqlite3 < $< >> _$@
	echo "</TABLE>" >> _$@
	mv _$@ $@

latex_832_vs_864.tex: \
  latex_832_vs_864.py \
  latex_832_vs_864.sql \
  _header_latex.sql \
  _header_files.sql \
  DISKPRINT_RESULTS.linked.log
	rm -f _$@ __$@
	sqlite3 < latex_832_vs_864.sql >> __$@
	$(PYTHON3) latex_832_vs_864.py __$@ > _$@
	mv _$@ $@ && rm __$@
