
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

ATTACH DATABASE 'doc_performance.db' AS dp;

CREATE TABLE doc_summary_stats AS
  SELECT
    doc_name,
    SUM(tp) AS tp,
    SUM(fp) AS fp,
    SUM(fn) AS fn,
    SUM(tn) AS tn
  FROM
    (
      SELECT
        *,
        CASE
          WHEN is_hit = 1 AND should_be_hit = 1 THEN 1
          ELSE 0
        END AS tp,
        CASE
          WHEN is_hit = 1 AND should_be_hit = 0 THEN 1
          ELSE 0
        END AS fp,
        CASE
          WHEN is_hit = 0 AND should_be_hit = 1 THEN 1
          ELSE 0
        END AS fn,
        CASE
          WHEN is_hit = 0 AND should_be_hit = 0 THEN 1
          ELSE 0
        END AS tn
      FROM
        dp.doc_performance
      WHERE
        NOT should_be_hit IS NULL
    ) AS d
  GROUP BY
    d.doc_name
;

CREATE TABLE doc_summary_ranking AS
  SELECT
    *,
    (tp + tn) / (1.0 * (tp + fp + fn + tn)) AS accuracy,
    (1.0 * tp) / (tp + fp) AS precision,
    (1.0 * tp) / (tp + fn) AS recall,
    (2.0 * tp) / (2 * tp + fp + fn) AS f1
  FROM
    doc_summary_stats
;
