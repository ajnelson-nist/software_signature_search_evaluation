
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

SELECT
  ROUND(max(recall), 4)
FROM
  searchers_with_nonzerolen_doc_counts
WHERE
  dataset = "evaluation" AND
  recall <> 1
;
