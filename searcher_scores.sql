
-- This software was developed at the National Institute of Standards
-- and Technology by employees of the Federal Government in the course
-- of their official duties. Pursuant to title 17 Section 105 of the
-- United States Code this software is not subject to copyright
-- protection and is in the public domain. NIST assumes no
-- responsibility whatsoever for its use by other parties, and makes
-- no guarantees, expressed or implied, about its quality,
-- reliability, or any other characteristic.
--
-- We would appreciate acknowledgement if the software is used.

ATTACH DATABASE 'rank_searchers.db' AS rs;
  CREATE TABLE searchers AS
    SELECT
      *
    FROM
      rs.searchers
  ;
DETACH DATABASE rs;

ATTACH DATABASE 'doc_statistics.db' AS ds;
  CREATE TABLE doc_statistics_id AS
    SELECT
      *
    FROM
      ds.doc_statistics_id
  ;
  CREATE TABLE doc_statistics_stat AS
    SELECT
      *
    FROM
      ds.doc_statistics_stat
  ;
DETACH DATABASE ds;

CREATE TEMPORARY TABLE temp_all_vsm_ids AS
  SELECT DISTINCT
    vsm_id
  FROM
    doc_statistics_id
;

CREATE TEMPORARY TABLE temp_nonzerolen_doc_counts AS
  SELECT
    vsm_id,
    COUNT(*) AS nonzerolen_doc_count
  FROM
    doc_statistics_stat
  WHERE
    doc_len <> 0
  GROUP BY
    vsm_id
;

CREATE TABLE nonzerolen_doc_counts AS
  SELECT
    ta.vsm_id,
    CASE
      WHEN tdc.nonzerolen_doc_count IS NULL THEN 0 ELSE tdc.nonzerolen_doc_count
    END AS nonzerolen_doc_count
  FROM
    temp_all_vsm_ids AS ta
      LEFT JOIN temp_nonzerolen_doc_counts AS tdc
      ON ta.vsm_id = tdc.vsm_id
;

CREATE TEMPORARY TABLE temp_zerolen_doc_counts AS
  SELECT
    vsm_id,
    COUNT(*) AS zerolen_doc_count
  FROM
    doc_statistics_stat
  WHERE
    doc_len = 0
  GROUP BY
    vsm_id
;

CREATE TABLE zerolen_doc_counts AS
  SELECT
    ta.vsm_id,
    CASE
      WHEN tdc.zerolen_doc_count IS NULL THEN 0 ELSE tdc.zerolen_doc_count
    END AS zerolen_doc_count
  FROM
    temp_all_vsm_ids AS ta
      LEFT JOIN temp_zerolen_doc_counts AS tdc
      ON ta.vsm_id = tdc.vsm_id
;

CREATE TABLE doc_len_counts AS
  SELECT
    nz.vsm_id,
    z.zerolen_doc_count,
    nz.nonzerolen_doc_count,
    (1.0 * nz.nonzerolen_doc_count) / (nz.nonzerolen_doc_count + z.zerolen_doc_count) AS proportion_nonzerolen
  FROM
    nonzerolen_doc_counts AS nz,
    zerolen_doc_counts AS z
  WHERE
    nz.vsm_id = z.vsm_id
;

CREATE TABLE searchers_with_nonzerolen_doc_counts AS
  SELECT
    s.*,
    CASE
      WHEN s.n_grams = "all" THEN "Whole path" ELSE "N-gram"
    END AS n_grams_collapsed,
    dlc.zerolen_doc_count,
    dlc.nonzerolen_doc_count,
    dlc.proportion_nonzerolen
  FROM
    searchers AS s,
    doc_len_counts AS dlc
  WHERE
    s.vsm_id = dlc.vsm_id
;
