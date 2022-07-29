# Local Transforms

[Documentation](https://docs.maltego.com/support/solutions/articles/15000017605-writing-local-transforms-in-python)

Transforms written using this library can be used as either local or server transforms.

To run a local transform from your project, you will need to pass the following arguments:

``` bash
project.py local <transform_name>
```

You can find the correct transform_name to use by running `python project.py list`.

## Caveats

The following values are not passed to local transforms, and will have dummy values in their place:

- `type`: `local.Unknown`
- `weight`: 100
- `slider`: 100
- `transformSettings`: {}
