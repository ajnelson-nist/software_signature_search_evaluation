
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

ATTACH DATABASE 'response_percentiles.db' AS percentiles;

.separator " & " " \\\\\n"

SELECT
  a.searcher_id,
  a.nonzerolen_doc_count,

  a.num_runs_in_ground_truth AS eval_num_runs_in_ground_truth,
  b.num_runs_in_ground_truth AS m57_num_runs_in_ground_truth,

  ROUND(a.recall,2) AS evaluation_recall,
  100 * ROUND(c.percentile,3) AS evaluation_recall_percentile,

  ROUND(b.recall,2) AS m57_recall,
  100 * ROUND(d.percentile,3) AS m57_recall_percentile
FROM
  (SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "evaluation") AS a,
  (SELECT * FROM searchers_with_nonzerolen_doc_counts WHERE dataset = "m57") AS b,
  percentiles.searcher_evaluation_recall_percentiles AS c,
  percentiles.searcher_m57_recall_percentiles AS d
WHERE
  a.searcher_id = b.searcher_id AND
  a.searcher_id = c.searcher_id AND
  a.searcher_id = d.searcher_id
ORDER BY
  b.recall DESC,
  a.recall DESC,
  b.nonzerolen_doc_count DESC
LIMIT 1
;
