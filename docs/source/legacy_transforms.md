# Legacy Transforms

[Documentation](https://docs.maltego.com/support/solutions/articles/15000018299-porting-old-trx-transforms-to-the-latest-version)

If you have old TRX transforms that are written as functions, they can be registered with the server using
the `maltego_trx.registry.register_transform_function` method.

In order to port your old transforms, make two changes:

1. Import the MaltegoTransform class from the `maltego_trx` package instead of from a local file.
2. Call the `register_transform_function` in order for the transform to be registered in your project.

For example

In the legacy transform file, change:

``` python
from Maltego import *

def old_transform(m):
```

To:

```python

from maltego_trx.maltego import MaltegoTransform


def old_transform(m):
    ...
```

In the `project.py` file add the following:

```python
from maltego_trx.registry import register_transform_function
from legacy_transform import trx_DNS2IP

register_transform_function(trx_DNS2IP)
```
