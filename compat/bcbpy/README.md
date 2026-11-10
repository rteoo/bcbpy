# bcbpy has moved to bcbdata

`bcbdata` is the maintained name of this Python client for Banco Central do
Brasil's SGS API. New applications should use `pip install bcbdata` and
`import bcbdata`.

This compatibility distribution installs the matching `bcbdata` release and
preserves the `bcbpy` public exports and the `client`, `codes`, `constants`, and
`artifacts` module paths. It contains no separate client implementation.
Existing function and exception identities are shared with `bcbdata`.

Older `bcbpy` releases remain available. A package rename does not transfer
PyPI release history or download counts.

See the [migration guide](https://github.com/rteoo/bcbdata/blob/main/docs/migration.md)
and [project README](https://github.com/rteoo/bcbdata#readme).
