# bcbpy has moved to bcb-data

`bcb-data` is the maintained name of this Python client for Banco Central do
Brasil's SGS API. New applications should use `pip install bcb-data` and
`import bcb_data`.

This compatibility distribution installs the matching `bcb-data` release and
preserves the `bcbpy` public exports and the `client`, `codes`, `constants`, and
`artifacts` module paths. It contains no separate client implementation.
Existing function and exception identities are shared with `bcb_data`.

To migrate an application:

```bash
pip install bcb-data
```

```python
from bcb_data import fetch_series
```

To retain existing `from bcbpy import ...` imports, upgrade with
`pip install --upgrade bcbpy`. Version 2.5.0 installs `bcb-data==2.5.0` and
forwards to the same implementation.

Older `bcbpy` releases remain available. A package rename does not transfer
PyPI release history or download counts.

See the [migration guide](https://github.com/rteoo/bcb-data/blob/main/docs/migration.md)
and [project README](https://github.com/rteoo/bcb-data#readme).
