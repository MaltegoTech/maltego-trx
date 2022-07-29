# Transform Registry

###### Added in 1.4.0 (July 2021)

The Transform Registry enables you to annotate Transforms with metadata like display name, description, input and output
entities as well as settings. The Transform Registry will automatically generate CSV files that you can import into the
pTDS and/or your iTDS.

## Configuring the Registry

You can configure your registry with all the info you would normally add for every transform/seed on a TDS. We recommend
creating your registry in an extra file, traditionally called `extensions.py`, to avoid circular imports.

```python
# extensions.py
from maltego_trx.decorator_registry import TransformRegistry

registry = TransformRegistry(
    owner="ACME Corporation",
    author="John Doe <johndoe@acme.com>",
    host_url="https://transforms.acme.org",
    seed_ids=["demo"]
)

# The rest of these attributes are optional

# metadata
registry.version = "0.1"

# transform suffix to indicate datasource
registry.display_name_suffix = " [ACME]"

# reference OAuth settings
registry.oauth_settings_id = ['github-oauth']

```

## Annotating Transforms

```python
# transforms/GreetPerson.py
...
from extensions import registry


@registry.register_transform(
    display_name='Greet Person',
    input_entity='maltego.Phrase',
    description='Returns a phrase greeting a person on the graph.',
    output_entities=['maltego.Phrase'],
    disclaimer='This disclaimer is optional and has to be accepted before this transform is run'
)
class GreetPerson(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        ...
```

**Pro Tip:** If the `display_name` is either `None` or `""`, the registry will try to create a display name from the
class name:

- `DNSToIP` 'DNS To IP'
- `GreetPerson` 'Greet Person'

## Transform Settings

You can declare transform settings in a central location and add them to the registry.

### Configuring Global Settings

These settings will apply to all transforms which can be very helpful for api keys.

```python
# settings.py
from maltego_trx.decorator_registry import TransformSetting

api_key_setting = TransformSetting(name='api_key',
                                   display_name='API Key',
                                   setting_type='string',
                                   global_setting=True)
```

```python
# extensions.py
from settings import api_key_setting

from maltego_trx.decorator_registry import TransformRegistry

registry = TransformRegistry(
    owner="ACME Corporation",
    author="John Doe <johndoe@acme.com>",
    host_url="https://transforms.acme.org",
    seed_ids=["demo"]
)

registry.global_settings = [api_key_setting]
```

#### Configuring Settings per Transform

Settings that aren't required for every transform have to be added to the `register_transform` decorator explicitly. To
access the setting on the request, use the `id` property, which will have the global prefix if it's a global setting.
The `name` property won't work on global settings.

```python
# settings.py
...

language_setting = TransformSetting(name='language',
                                    display_name="Language",
                                    setting_type='string',
                                    default_value='en',
                                    optional=True,
                                    popup=True)
```

```python
# transforms/GreetPerson.py
...
from settings import language_setting

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="Greet Person",
                             input_entity="maltego.Phrase",
                             description='Returns a phrase greeting a person on the graph.',
                             settings=[language_setting])
class GreetPerson(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        language = request.getTransformSetting(language_setting.id)
        ...
```

### Exporting the TDS Configuration

To export the configurations, use the registry methods `write_transforms_config()` and `write_settings_config()`. These
methods have to executed after they have been registered with the TRX server.

```python
# project.py

import sys
import transforms

from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import application
from maltego_trx.handler import handle_run

# register_transform_function(transform_func)
from extensions import registry

register_transform_classes(transforms)

registry.write_transforms_config()
registry.write_settings_config()

handle_run(__name__, sys.argv, application)
```

## Generating an `.mtz` config with your local Transforms

Since `maltego-trx>=1.6.0` you can generate an `.mtz` config file with your local transforms.

If you're already using the `TransformRegistry`, just invoke the `write_local_config()` method.

```python
# project.py

registry.write_local_mtz()
```

This will create a file called `local.mtz` in the current directory. You can then import this file into Maltego and
start using your local transforms faster. Just remember that settings are not passed to local transforms.

The method takes in the same arguments as the interface in the Maltego client.
If you are using a `virtualenv` environment, you might want to change the `command` argument to use that.

```bash
# project.py

registry.write_local_mtz(
    mtz_path: str = "./local.mtz", # path to the local .mtz file
    working_dir: str = ".",
    command: str = "python3", # for a venv you might want to use `./venv/bin/python3`
    params: str = "project.py",
    debug: bool = True
)
```
