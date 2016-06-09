
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

.read _header_html.sql

SELECT
  COUNT(*) AS tally,
  ha1.filename
FROM
  vista64.hive_analysis AS ha1,
  vista64.cell_analysis as ca1
WHERE
  ca1.hive_id = ha1.hive_id AND
  ca1.cellname IN (
    SELECT
      cellname
    FROM
      win864.cell_analysis
  )
GROUP BY
  ha1.filename
;
