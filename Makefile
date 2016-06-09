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
GTIME ?= /opt/local/bin/gtime
PYTHON3 ?= python3.4
SEVENZIP ?= 7z
SHELL = /bin/bash
export PYTHON3

all: dist

.PHONY: \
  alt-download \
  alt-generate \
  check \
  check-check_printed_etids_for_labels \
  check-ground_truth \
  check-tests \
  dist \
  dist-ground_truth \
  download \
  download-brown \
  extra \
  magnum_opus-extra \
  mult_results-extra \
  os_overlap_hives-recursive

Objects.py: \
  SUBMODULES_CHECKED_OUT.log
	touch $@ #Ensure timestamp is up to date.

PY3_MATPLOTLIB:
	$(PYTHON3) -c "import seaborn"
	touch $@

#Instead of calling bootstrap.sh, this really just needs the submodules initialized.  TODO Track the submodules in the diskprint workflow as proper submodules.
SUBMODULES_CHECKED_OUT.log:
	git submodule init
	git submodule update --recursive
	cd deps/diskprint_workflow; ./git_submodule_init.sh
	cd deps/diskprint_workflow/deps/regxml_extractor.git; git submodule init
	cd deps/diskprint_workflow/deps/regxml_extractor.git; git submodule update
	touch $@

#The alt rules behave partially like the download target.
alt-download: \
  SUBMODULES_CHECKED_OUT.log \
  sequences/namedsequence.db
	$(MAKE) -C diskprint_extraction_workflow_results/data_diskprints/make_registry_diff_db_alt download
	$(MAKE) -C diskprint_extraction_workflow_results/data_diskprints alt

alt-generate: \
  SUBMODULES_CHECKED_OUT.log \
  diskprint_extraction_workflow_results/data_diskprints/make_registry_diff_db_alt/differ.cfg \
  sequences/namedsequence.db
	$(MAKE) -C diskprint_extraction_workflow_results/data_diskprints/make_registry_diff_db_alt generate
	$(MAKE) -C diskprint_extraction_workflow_results/data_diskprints alt

apps_printed.html: apps_printed.sql slice.db etid_to_productname.db
	echo "<table>" > _$@
	echo "  <thead><tr><th>Product Name</th></tr></thead>" >> _$@
	echo "  <tfoot></tfoot>" >> _$@
	echo "  <tbody>" >> _$@
	sqlite3 slice.db < apps_printed.sql >> _$@
	echo "  </tbody>" >> _$@
	echo "</table>" >> _$@
	mv _$@ $@

check: \
  check-check_printed_etids_for_labels \
  check-ground_truth \
  check-tests

check-check_printed_etids_for_labels: \
  check_printed_etids_for_labels.py \
  etid_to_productname.db \
  slice.db
	$(PYTHON3) check_printed_etids_for_labels.py $(DEBUG_FLAG) etid_to_productname.db slice.db

check-ground_truth: \
  ground_truth/ground_truth.mk.done.log
	$(MAKE) -C ground_truth check

check-tests:
	$(MAKE) -C tests check

demo-prereqs: \
  diskprint_extraction_workflow_results/data_evaluation/inflate.done.log \
  diskprint_extraction_workflow_results/data_m57/inflate.done.log \
  magnum_opus.mk
	$(MAKE) -f magnum_opus.mk \
	  query/data_evaluation/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/stop_list_baseline/experiment1-15.db \
	  signature_searcher_training/data_training/sequences_installclose/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/combinator_intersection/stop_list_bp/versions_grouped/score_selector_min/signature_searcher.pickle \
	  search_scores/data_evaluation/sequences_installclose/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/combinator_intersection/stop_list_bp/pickle_manifest.txt

#This Signature Searcher was hand-selected with this SQL query, solely for illustration purposes and not as an endorsement of superior performance:
#SELECT searcher_id, tp FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "evaluation" AND stop_list <> "none" AND n_grams = "all" ORDER BY precision DESC, tp DESC, recall DESC LIMIT 20;
demo.html: \
  etid_to_productname.db \
  ground_truth/data_evaluation/docs_by_app/versions_grouped/ground_truth.db \
  query/data_evaluation/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/stop_list_baseline/experiment1-15.db \
  search_scores/data_evaluation/sequences_installclose/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/combinator_intersection/stop_list_bp/experiment1-15.pickle \
  signature_search_report.py \
  signature_searcher_training/data_training/sequences_installclose/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/combinator_intersection/stop_list_bp/versions_grouped/score_selector_min/signature_searcher.pickle
	rm -f _$@
	$(PYTHON3) signature_search_report.py \
	  $(DEBUG_FLAG) \
	  --short-tables \
          --ground-truth-db ground_truth/data_evaluation/docs_by_app/versions_grouped/ground_truth.db \
          --ground-truth-node-id experiment1-15 \
	  etid_to_productname.db \
	  signature_searcher_training/data_training/sequences_installclose/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/combinator_intersection/stop_list_bp/versions_grouped/score_selector_min/signature_searcher.pickle \
	  term_db/data_evaluation/paths_normalized/n_grams_all/experiment1-15.db \
	  query/data_evaluation/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/stop_list_baseline/experiment1-15.db \
	  search_scores/data_evaluation/sequences_installclose/n_grams_all/stop_list_n_gram_strategy_n_gram_blacklist/paths_normalized/docs_by_app/combinator_intersection/stop_list_bp/experiment1-15.pickle \
	  _$@
	mv _$@ $@

deps/brownzipf/brown_downloaded.log: \
  deps/brownzipf/demo.py
	$(MAKE) -C deps/brownzipf brown_downloaded.log

deps/brownzipf/demo.png: \
  deps/brownzipf/brown_downloaded.log \
  deps/brownzipf/demo.py
	$(MAKE) -C deps/brownzipf demo.png

deps/brownzipf/demo.py: \
  SUBMODULES_CHECKED_OUT.log
	touch $@ #Ensure timestamp is up to date

dfxml.py: \
  SUBMODULES_CHECKED_OUT.log
	touch $@ #Ensure timestamp is up to date

differ_func_library.py: \
  SUBMODULES_CHECKED_OUT.log
	touch $@ #Ensure timestamp is up to date

diskprint_extraction_workflow_results/data_diskprints/make_registry_diff_db_alt/differ.cfg:
	$(MAKE) -C diskprint_extraction_workflow_results/data_diskprints/make_registry_diff_db_alt differ.cfg

dist: \
  deps/brownzipf/demo.png \
  dist-ground_truth \
  export_results.txt \
  hive_class_contributions.html \
  hive_class_contributions.tex \
  hivexml_failures.tex \
  hivexml_status.tex \
  invisible_secrets_eyeball_stats.txt \
  m57_counts_fs.pdf \
  m57_counts_reg.pdf \
  max_doc_counts/subset_all/searcher_scores_max_doc_counts.tex \
  mult_results.mk.done.log \
  os_disjunctions_normalized.html \
  os_disjunctions_normalized.tex \
  os_disjunctions_raw.html \
  os_disjunctions_raw.tex \
  os_overlap_hives/latex_832_vs_864.tex \
  print_status_01_19.tex \
  print_status_20.tex \
  top_by_precision_corpora_main_effects.tex \
  top_by_precision_evaluation.tex \
  top_by_precision_m57.tex \
  top_by_recall_corpora_main_effects.tex \
  top_by_recall_evaluation.tex \
  top_by_recall_m57.tex \
  zipfian_plots/all.done.log
	@echo "Results ready to export."

dist-ground_truth: \
  etid_to_productname.db \
  ground_truth/first_appearance_evaluation_image.py \
  ground_truth/ground_truth.mk.done.log \
  ground_truth/tablify_evaluation_ground_truth.py
	$(MAKE) -C ground_truth dist

diskprint_extraction_workflow_results/data_diskprints/inflate.done.log:
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_diskprints/extraction_workflow_results_diskprints.zip.downloaded.log: \
  diskprint_extraction_workflow_results/data_diskprints/extraction_workflow_results_diskprints.zip
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_evaluation/extraction_workflow_results_evaluation.zip:
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_evaluation/extraction_workflow_results_evaluation.zip.downloaded.log: \
  diskprint_extraction_workflow_results/data_evaluation/extraction_workflow_results_evaluation.zip
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_evaluation/inflate.done.log: \
  diskprint_extraction_workflow_results/data_evaluation/extraction_workflow_results_evaluation.zip.downloaded.log
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_m57/extraction_workflow_results_m57.zip:
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_m57/extraction_workflow_results_m57.zip.downloaded.log: \
  diskprint_extraction_workflow_results/data_m57/extraction_workflow_results_m57.zip
	$(MAKE) -C $$(dirname $@) $$(basename $@)

diskprint_extraction_workflow_results/data_m57/inflate.done.log: \
  diskprint_extraction_workflow_results/data_m57/extraction_workflow_results_m57.zip.downloaded.log
	$(MAKE) -C $$(dirname $@) $$(basename $@)

#The dependency on searcher_scores.db is a proxy for some targets created in magnum_opus.py.
doc_performance.db: \
  doc_performance_db.py \
  searcher_scores.db
	rm -f _$@
	$(GTIME) --verbose --output=$@.time.log $(PYTHON3) doc_performance_db.py $(DEBUG_FLAG) signature_searcher_measurement_manifest.txt _$@
	mv _$@ $@

download: \
  deps/brownzipf/brown_downloaded.log \
  diskprint_extraction_workflow_results/data_diskprints/extraction_workflow_results_diskprints.zip.downloaded.log \
  diskprint_extraction_workflow_results/data_evaluation/extraction_workflow_results_evaluation.zip.downloaded.log \
  diskprint_extraction_workflow_results/data_m57/extraction_workflow_results_m57.zip.downloaded.log \
  etid_to_productname.db \
  slice.db

download-brown: \
  deps/brownzipf/brown_downloaded.log

etid_to_productname.db:
	wget http://www.nsrl.nist.gov/diskprint_data/etid_to_productname.db.sha512
	wget -O _$@ http://www.nsrl.nist.gov/diskprint_data/etid_to_productname.db
	test "x$$(openssl dgst -sha512 "_$@" | awk '{print tolower($$(NF))}')" == "x$$(cat $@.sha512)"
	mv _$@ $@

extra: \
  apps_printed.html \
  demo.html \
  doc_performance.db \
  hivexml_status/data_diskprints/hivexml_status.db \
  hivexml_status/data_evaluation/hivexml_status.html \
  hivexml_status/data_m57/hivexml_status.html \
  hivexml_status/data_training/hivexml_status.html \
  magnum_opus-extra \
  mult_results-extra \
  os_overlap_hives-recursive \
  print_status.html \
  print_status.tex \
  score_table.mk.done.log \
  sequences_printed.html

ground_truth/ground_truth.mk.done.log: \
  differ_func_library.py \
  etid_to_productname.db \
  experiments/m57_roussev_dfrws12/application_appearances.py \
  experiments/m57_roussev_dfrws12/db.py \
  ground_truth/cartesian_ground_truth_completion.py \
  ground_truth/check_ground_truth_negative_m57.sh \
  ground_truth/check_ground_truth_positive_doc_names.sh \
  ground_truth/check_ground_truth_uniqueness.sh \
  ground_truth/check_versions_counts_consistent.sh \
  ground_truth/ground_truth.py \
  ground_truth/ground_truth_evaluation_image_app.sql \
  ground_truth/ground_truth_evaluation_image_osapp.sql \
  ground_truth/ground_truth_grouped.py \
  ground_truth/ground_truth_mk.py \
  ground_truth/m57_ground_truth_completion.py \
  m57_meta.py \
  sequences/namedsequence.db \
  slice.db
	$(MAKE) -C ground_truth $$(basename $@)
	touch $@ #Guarantee timestamp is up to date

hive_class_contributions.db: \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  hive_class_contributions_db.py \
  normalizer.py \
  slice.db
	rm -f _$@
	$(PYTHON3) hive_class_contributions_db.py slice.db diskprint_extraction_workflow_results/data_diskprints/by_node _$@ 2>$@.err.log
	mv _$@ $@

hive_class_contributions.html: \
  hive_class_contributions.db \
  hive_class_contributions_table.py \
  normalizer.py
	rm -f _$@
	$(PYTHON3) hive_class_contributions_table.py --html hive_class_contributions.db _$@
	mv _$@ $@

hive_class_contributions.tex: \
  hive_class_contributions.db \
  hive_class_contributions_table.py \
  normalizer.py
	rm -f _$@
	$(PYTHON3) hive_class_contributions_table.py --latex hive_class_contributions.db _$@
	mv _$@ $@

hivexml_failures.db: \
  hivexml_status/data_evaluation/hivexml_status.db \
  hivexml_status/data_m57/hivexml_status.db \
  hivexml_status/data_training/hivexml_status.db \
  hivexml_failures.py
	rm -f _$@
	$(PYTHON3) hivexml_failures.py $(DEBUG_FLAG) _$@ hivexml_status/data_{evaluation,m57,training}/hivexml_status.db
	mv _$@ $@

hivexml_failures.tex: \
  hivexml_failures.db \
  hivexml_failures_texify.py
	rm -f _$@
	$(PYTHON3) hivexml_failures_texify.py hivexml_failures.db _$@
	mv _$@ $@

#For inspecting all of the posted data.
hivexml_status/data_diskprints/hivexml_status.db: \
  Objects.py \
  dfxml.py \
  differ_func_library.py \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  hivexml_status_db_diskprints.py \
  hivexml_status_db_library.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_db_diskprints.py $(DEBUG_FLAG) diskprint_extraction_workflow_results/data_diskprints $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_evaluation/hivexml_status.db: \
  Objects.py \
  dfxml.py \
  diskprint_extraction_workflow_results/data_evaluation/inflate.done.log \
  hivexml_status_db_evaluation.py \
  hivexml_status_db_library.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_db_evaluation.py $(DEBUG_FLAG) diskprint_extraction_workflow_results/data_evaluation/by_node $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_evaluation/hivexml_status.html: \
  hivexml_status/data_evaluation/hivexml_status.db \
  hivexml_status_report.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_report.py $(DEBUG_FLAG) --html hivexml_status/data_evaluation/hivexml_status.db $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_evaluation/hivexml_status.tex: \
  hivexml_status/data_evaluation/hivexml_status.db \
  hivexml_status_report.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_report.py $(DEBUG_FLAG) --tex hivexml_status/data_evaluation/hivexml_status.db $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_m57/hivexml_status.db: \
  Objects.py \
  dfxml.py \
  diskprint_extraction_workflow_results/data_m57/inflate.done.log \
  hivexml_status_db_library.py \
  hivexml_status_db_m57.py \
  m57_meta.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_db_m57.py $(DEBUG_FLAG) diskprint_extraction_workflow_results/data_m57/by_node $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_m57/hivexml_status.html: \
  hivexml_status/data_m57/hivexml_status.db \
  hivexml_status_report.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_report.py $(DEBUG_FLAG) --html hivexml_status/data_m57/hivexml_status.db $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_m57/hivexml_status.tex: \
  hivexml_status/data_m57/hivexml_status.db \
  hivexml_status_report.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_report.py $(DEBUG_FLAG) --tex hivexml_status/data_m57/hivexml_status.db $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_training/hivexml_status.db: \
  Objects.py \
  dfxml.py \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  sequences/namedsequence.db \
  hivexml_status_db_training.py \
  hivexml_status_db_library.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_db_training.py $(DEBUG_FLAG) sequences/namedsequence.db diskprint_extraction_workflow_results/data_diskprints $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_training/hivexml_status.html: \
  hivexml_status/data_training/hivexml_status.db \
  hivexml_status_report.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_report.py $(DEBUG_FLAG) --html hivexml_status/data_training/hivexml_status.db $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status/data_training/hivexml_status.tex: \
  hivexml_status/data_training/hivexml_status.db \
  hivexml_status_report.py
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	$(PYTHON3) hivexml_status_report.py $(DEBUG_FLAG) --tex hivexml_status/data_training/hivexml_status.db $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

hivexml_status.tex: \
  hivexml_status/data_evaluation/hivexml_status.tex \
  hivexml_status/data_m57/hivexml_status.tex \
  hivexml_status/data_training/hivexml_status.tex \
  hivexml_status_report_glom.py
	rm -f _$@
	$(PYTHON3) hivexml_status_report_glom.py $(DEBUG_FLAG) _$@ hivexml_status/data_{evaluation,m57,training}/hivexml_status.tex
	mv _$@ $@

invisible_secrets_eyeball_stats.txt: \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  invisible_secrets_eyeball_stats.py \
  sequences/namedsequence.db \
  slice.db
	rm -f _$@
	$(PYTHON3) invisible_secrets_eyeball_stats.py sequences/namedsequence.db slice.db diskprint_extraction_workflow_results/data_diskprints 2>_$@
	mv _$@ $@

m57_counts.mk: \
  diskprint_extraction_workflow_results/data_m57/inflate.done.log \
  m57_counts_mk.py \
  m57_meta.py
	rm -f _$@
	$(PYTHON3) m57_counts_mk.py $(DEBUG_FLAG) diskprint_extraction_workflow_results/data_m57/by_node _$@
	mv -f _$@ $@

m57_counts.mk.done.log: m57_counts.mk
	$(MAKE) -f m57_counts.mk
	touch $@

m57_counts_fs.pdf: \
  Objects.py \
  PY3_MATPLOTLIB \
  dfxml.py \
  m57_counts.mk.done.log \
  m57_counts_plot.py
	rm -f _$@
	$(PYTHON3) m57_counts_plot.py $(DEBUG_FLAG) m57_counts fs _$@
	mv _$@ $@

m57_counts_reg.pdf: \
  PY3_MATPLOTLIB \
  dfxml.py \
  m57_counts.mk.done.log \
  m57_counts_plot.py
	rm -f _$@
	$(PYTHON3) m57_counts_plot.py $(DEBUG_FLAG) m57_counts reg _$@
	mv _$@ $@

magnum_opus.mk: \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  experiments/node_id_lists/experiment1 \
  ground_truth/ground_truth.mk.done.log \
  m57_meta.py \
  magnum_opus.py \
  sequences/namedsequence.db
	rm -f _$@
	$(PYTHON3) magnum_opus.py $(DEBUG_FLAG) sequences/namedsequence.db experiments/node_id_lists/experiment1 diskprint_extraction_workflow_results/data_diskprints diskprint_extraction_workflow_results/data_evaluation diskprint_extraction_workflow_results/data_m57 _$@
	mv _$@ $@

magnum_opus-extra: \
  magnum_opus.mk \
  searcher_scores.db
	$(MAKE) -f magnum_opus.mk extra

max_doc_counts/subset_all/searcher_scores_max_doc_counts.tex: \
  max_doc_counts/subset_all/searcher_scores_max_doc_counts.sql \
  searcher_scores.db
	mkdir -p $$(dirname $@)
	rm -f $$(dirname $@)/_$$(basename $@)
	sqlite3 searcher_scores.db < $< > $$(dirname $@)/_$$(basename $@)
	mv $$(dirname $@)/_$$(basename $@) $@

mult_results-extra: \
  doc_performance.db \
  magnum_opus-extra \
  mult_results.mk.done.log
	$(MAKE) -f mult_results.mk extra

mult_results.mk: \
  SignatureSearcher_ppp.py \
  mult_results.py
	rm -f _$@
	$(PYTHON3) mult_results.py _$@
	mv _$@ $@

mult_results.mk.done.log: \
  PY3_MATPLOTLIB \
  cumulative_histogram.py \
  mult_results.mk \
  overview_scatter_hist.py \
  perfect_searchers_metric.sql.in \
  perfect_searchers_metric_breakout.sql.in \
  response_percentiles.db \
  scatter_plot.py \
  searcher_scores.db \
  searcher_scores_pair_grid.py \
  talk_searcher_scores_pair_grid.py \
  top_n_m57_generator.py
	$(MAKE) -f mult_results.mk
	touch $@

os_disjunctions_normalized.html: \
  os_disjunctions_normalized.pickle \
  os_disjunctions_table.py
	rm -f _$@
	$(PYTHON3) os_disjunctions_table.py $(DEBUG_FLAG) --html os_disjunctions_normalized.pickle _$@
	mv _$@ $@

os_disjunctions_normalized.pickle: \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  normalizer.py \
  os_disjunctions_pickle.py
	rm -f _$@
	$(PYTHON3) os_disjunctions_pickle.py $(DEBUG_FLAG) --normalize diskprint_extraction_workflow_results/data_diskprints/by_node _$@
	mv _$@ $@

os_disjunctions_normalized.tex: \
  os_disjunctions_normalized.pickle \
  os_disjunctions_table.py
	rm -f _$@
	$(PYTHON3) os_disjunctions_table.py $(DEBUG_FLAG) --latex os_disjunctions_normalized.pickle _$@
	mv _$@ $@

os_disjunctions_raw.html: \
  os_disjunctions_raw.pickle \
  os_disjunctions_table.py
	rm -f _$@
	$(PYTHON3) os_disjunctions_table.py $(DEBUG_FLAG) --html os_disjunctions_raw.pickle _$@
	mv _$@ $@

os_disjunctions_raw.pickle: \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log \
  normalizer.py \
  os_disjunctions_pickle.py
	rm -f _$@
	$(PYTHON3) os_disjunctions_pickle.py $(DEBUG_FLAG) diskprint_extraction_workflow_results/data_diskprints/by_node _$@
	mv _$@ $@

os_disjunctions_raw.tex: \
  os_disjunctions_raw.pickle \
  os_disjunctions_table.py
	rm -f _$@
	$(PYTHON3) os_disjunctions_table.py $(DEBUG_FLAG) --latex os_disjunctions_raw.pickle _$@
	mv _$@ $@

os_overlap_hives-recursive: \
  os_overlap_hives/latex_832_vs_864.tex
	$(MAKE) -C os_overlap_hives

os_overlap_hives/latex_832_vs_864.tex: \
  diskprint_extraction_workflow_results/data_diskprints/inflate.done.log
	$(MAKE) -C os_overlap_hives latex_832_vs_864.tex

print_status.html: \
  etid_to_productname.db \
  installclose_sequence_table.py \
  sequences/namedsequence.db
	rm -f _$@
	$(PYTHON3) installclose_sequence_table.py $(DEBUG_FLAG) --html sequences/namedsequence.db etid_to_productname.db _$@
	mv _$@ $@

print_status.tex: \
  etid_to_productname.db \
  installclose_sequence_table.py \
  sequences/namedsequence.db
	rm -f _$@
	$(PYTHON3) installclose_sequence_table.py $(DEBUG_FLAG) --latex sequences/namedsequence.db etid_to_productname.db _$@
	mv _$@ $@

print_status_01_19.tex: \
  etid_to_productname.db \
  installclose_sequence_table.py \
  sequences/namedsequence.db
	rm -f _$@
	$(PYTHON3) installclose_sequence_table.py $(DEBUG_FLAG) --count=19 --latex sequences/namedsequence.db etid_to_productname.db _$@
	mv _$@ $@

print_status_20.tex: \
  etid_to_productname.db \
  installclose_sequence_table.py \
  sequences/namedsequence.db
	rm -f _$@
	$(PYTHON3) installclose_sequence_table.py $(DEBUG_FLAG) --skip=19 --latex sequences/namedsequence.db etid_to_productname.db _$@
	mv _$@ $@

response_percentiles.db: \
  cumsum_table.py \
  searcher_scores.db
	rm -f _$@
	$(PYTHON3) cumsum_table.py searcher_scores.db _$@
	mv _$@ $@

score_table.mk: \
  magnum_opus.py \
  score_table_mk.py
	rm -f _$@
	$(PYTHON3) score_table_mk.py _$@
	mv _$@ $@

score_table.mk.done.log: \
  PY3_MATPLOTLIB \
  score_table.mk \
  score_table.py \
  searcher_scores.db
	$(MAKE) -f score_table.mk
	touch $@

searcher_scores.db: \
  SignatureSearcher.py \
  TFIDFEngine.py \
  cell_parent_db.py \
  cell_parent_db_rollup.py \
  diskprint_extraction_workflow_results/data_evaluation/inflate.done.log \
  diskprint_extraction_workflow_results/data_m57/inflate.done.log \
  doc_statistics_db.py \
  dump_parent_map.py \
  extract_threshold_dictionary.py \
  magnum_opus.mk \
  measure_SignatureSearcher.py \
  n_gram_derivation_pickle.py \
  n_grammer.py \
  normalizer.py \
  rank_searchers_db.py \
  reg_db_to_term_list.py \
  run_model_on_queries.py \
  searcher_scores.sql \
  slice.db \
  stop_list/none.db \
  stop_list_inconsistent.py \
  stop_list_normalized.py \
  stoplisted_query.py \
  train_SignatureSearcher.py \
  vsm_set_theory_ops.py
	$(MAKE) -f magnum_opus.mk $@
	touch $@ #Guarantee timestamp is up to date

sequences/namedsequence.db:
	$(MAKE) -C sequences namedsequence.db

sequences_printed.html: \
  etid_to_productname.db \
  sequences_printed.sql \
  sequences/namedsequence.db \
  slice.db
	echo "<table>" > _$@
	echo "  <thead><tr><th>Sequence Label</th><th>OS</th><th>Application</th><th>Version</th><th>Slice ID</th><th>Slice Type</th></tr></thead>" >> _$@
	echo "  <tfoot></tfoot>" >> _$@
	echo "  <tbody>" >> _$@
	sqlite3 sequences/namedsequence.db < sequences_printed.sql >> _$@
	echo "  </tbody>" >> _$@
	echo "</table>" >> _$@
	mv _$@ $@

slice.db:
	wget http://www.nsrl.nist.gov/diskprint_data/slice.db.sha512
	wget -O _$@ http://www.nsrl.nist.gov/diskprint_data/slice.db
	test "x$$(openssl dgst -sha512 "_$@" | awk '{print tolower($$(NF))}')" == "x$$(cat $@.sha512)"
	mv _$@ $@

stop_list/none.db: stop_list_none.sql
	mkdir -p stop_list
	rm -f stop_list/_none.db
	sqlite3 stop_list/_none.db < stop_list_none.sql
	mv stop_list/_none.db stop_list/none.db

top_by_precision_corpora_main_effects.tex: \
  top_by_precision_corpora_main_effects.sql \
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@

top_by_precision_evaluation.tex: \
  top_by_precision_evaluation.sql \
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@

top_by_precision_m57.tex: \
  top_by_precision_m57.sql \
  response_percentiles.db \
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@

top_by_recall_corpora_main_effects.tex: \
  top_by_recall_corpora_main_effects.sql \
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@

top_by_recall_evaluation.tex: \
  top_by_recall_evaluation.sql \
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@

top_by_recall_m57.tex: \
  top_by_recall_m57.sql \
  response_percentiles.db \
  searcher_scores.db
	rm -f _$@
	sqlite3 searcher_scores.db < $< > _$@
	mv _$@ $@

zipfian_plots/all.done.log: \
  searcher_scores.db \
  zipfian_plots/n_gram_rank_dist.py \
  zipfian_plots/plots_mk.py
	$(MAKE) -C zipfian_plots
