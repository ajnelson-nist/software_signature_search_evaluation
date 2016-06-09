#!/usr/bin/env python3

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

"""
A library for converting Registry paths into n-grams.
"""

__version__ = "0.1.1"

num_aux_queries_run = 0

#Key: Absolute cell path.
#Value: Pair, (parent cell path, basename).
parent_map = dict()

def ingest_into_parent_map(standalone_cursor, cellpath):
    """
    Recursive function.

    Parameter notes:
    standalone_cursor: A cursor that can run SELECTs without side effects in the calling program.  The cursor should be for a database where the cell parent table is in the ATTACHed database aliased "cp".
    """
    global parent_map
    global num_aux_queries_run
    #_logger.debug("term = %r." % term)
    if cellpath is None:
        return
    if cellpath in parent_map:
        return
    num_aux_queries_run += 1
    standalone_cursor.execute("""\
SELECT
  parentpath,
  basename
FROM
  cp.cell_parent
WHERE
  cellpath = ?
;""", (cellpath,))
    _row = standalone_cursor.fetchone()
    if _row is None:
        raise ValueError("Could not find parent entry for cellpath %r." % cellpath)
    parent_map[cellpath] = (_row["parentpath"], _row["basename"])
    ingest_into_parent_map(standalone_cursor, _row["parentpath"])

def basename_chain(term):
    """
    Generator.  Yields path components of term in reverse order (child to grandest-parent).
    """
    global parent_map
    current_term = term
    while not current_term is None:
        (current_parent, current_basename) = parent_map[current_term]
        yield current_basename
        current_term = current_parent

def n_grams(term, n_gram_length, last_n_gram_only=False):
    r"""
    Converts a term to its component n grams.

    E.g. bigrams of "\foo\bar\baz" are "\foo", "foo\bar", "bar\baz".
    """
    #NOTE The root path may not be coming out ("\foo" example), but it's going to be common and cancelled out anyway, so that's fine.
    assert isinstance(n_gram_length, int)
    n_ring_reversed = []
    #_logger.debug("term = %r." % term)
    for basename in basename_chain(term):
        n_ring_reversed.append(basename)
        #_logger.debug("basename = %r." % basename)
        #_logger.debug("n_ring_reversed = %r." % n_ring_reversed)
        if len(n_ring_reversed) == n_gram_length:
            yield "\\".join(n_ring_reversed[::-1]) #Reverse

            #Since these are popped out in reverse (due to basename-based operation), we just don't loop if we're only looking for the last n gram of the term.
            if last_n_gram_only:
                break

            n_ring_reversed.pop(0)
