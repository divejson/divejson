"""Tools for DiveJSON, an open dive-log interchange format.

The normative specification lives in ``spec/divejson.md``; the JSON Schema in
``schema/1.0/divejson.schema.json``. This package implements the reference tools:
``validate`` — the schema pass plus the requirements the spec lists as beyond-schema —
and ``uddf``, which reads UDDF logbooks into conforming documents. Both are importable
functions; ``cli`` is a thin wrapper over them.
"""

__version__ = "0.1.0"

SPEC_VERSION = "1.0"
