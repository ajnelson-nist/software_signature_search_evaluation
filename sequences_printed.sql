
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

.mode html

ATTACH DATABASE 'etid_to_productname.db' AS etp;
ATTACH DATABASE 'slice.db' AS slice;

SELECT DISTINCT
  sequencelabel,
  eo.ProductName,
  ea.ProductName,
  ea.Version,
  s.sliceid,
  s.slicetype
FROM
  namedsequence AS ns,
  slice.slice AS s,
  etp.etid_to_productname AS ea,
  etp.etid_to_productname AS eo
WHERE
  ns.osetid = s.osetid AND
  ns.appetid = s.appetid AND
  ns.sliceid = s.sliceid AND
  s.appetid = ea.ETID AND
  s.osetid = eo.ETID
ORDER BY
  ns.sequencelabel,
  s.osetid,
  s.appetid,
  s.sliceid
;
