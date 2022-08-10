# Maltego TRX Python Library

[![Runs with Python3.6 - Python3.10](https://github.com/paterva/maltego-trx/actions/workflows/pythonx-boot-check.yaml/badge.svg)](https://github.com/paterva/maltego-trx/actions/workflows/pythonx-boot-check.yaml)
[![PyTest with Python3.6 - Python3.10](https://github.com/paterva/maltego-trx/actions/workflows/pythonx-pytest.yaml/badge.svg)](https://github.com/paterva/maltego-trx/actions/workflows/pythonx-pytest.yaml)
[![Sonatype Jake](https://github.com/paterva/maltego-trx/actions/workflows/sonatype-jack.yml/badge.svg)](https://github.com/paterva/maltego-trx/actions/workflows/sonatype-jack.yml)

## Release Notes

__1.6.0__: Automatically generate am `.mtz` for your local transforms

__1.5.2__: Add logging output for invalid / missing params in xml serialization

__1.5.1__: Add ignored files to starter and use README for pypi

__1.5.0__: XML Serialization via `ElementTree` instead of string interpolation

__1.4.4__: Added skeletons for csv export in template dir and made project.py application import compatible with docs

__1.4.0 + 1.4.1:__ Both versions are incompatible with python3.7 and lower.

__1.4.2__: Fixed python3.6 incompatibility

## Getting Started

_Note: Support for Python 2 has been officially discontinued as of July 2021. Please use Python 3.6 or higher to use
up-to-date versions of Maltego TRX._

To install the trx library run the following command:

``` bash
pip install maltego-trx
```

After installing, you can create a new project by running the following command:

``` bash
maltego-trx start new_project
```

This will create a folder new_project with the recommended project structure.

If you want to copy the starter files to your current directory, run the following command:

```bash
maltego-trx init
```

Alternatively, you can copy either the `gunicorn` or `apache` example projects from the `demo` directory. These also
include Dockerfile and corresponding docker-compose configuration files for production deployment.

**Adding a Transform:**

Add a new transform by creating a new python file in the "transforms" folder of your directory.

Any file in the folder where the **class name matches the filename**, and the class inherits from Transform, will
automatically be discovered and added to your server.

A simple transform would look like the following:

`new_project/transforms/GreetPerson.py`

``` python
from maltego_trx.entities import Phrase
from maltego_trx.transform import DiscoverableTransform


class GreetPerson(DiscoverableTransform):
    """
    Returns a phrase greeting a person on the graph.
    """

    @classmethod
    def create_entities(cls, request, response):
        person_name = request.Value

        response.addEntity(Phrase, "Hi %s, nice to meet you!" % person_name)
```

## Running The Transform Server

### For Development

You can start the development server, by running the following command:

``` bash
python project.py runserver
```

This will start up a development server that automatically reloads every time the code is changed.

### For Production

You can run a gunicorn transform server, after installing gunicorn on the host machine and then running the command:

``` bash
gunicorn --bind=0.0.0.0:8080 --threads=25 --workers=2 project:application
```

*For publicly accessible servers, it is recommended to run your Gunicorn server behind proxy servers such as Nginx.*

## Run a Docker Transform server

The `demo` folder provides an example project. The Docker files given can be used to set up and run your project in
Docker.

The Dockerfile and docker-compose file can be used to easily set up and run a development transform server.

If you have copied the `docker-compose.yml`, `Dockerfile` and `prod.yml` files into your project, then you can use the
following commands to run the server in Docker.

Run the following to start the development server:

``` bash
docker-compose up
```

Run the following command to run a production gunicorn server:

``` bash
docker-compose -f prod.yml up --build
```

*For publicly accessible servers, it is recommended to run your Gunicorn server behind proxy servers such as Nginx.*

## Local Transforms

[Documentation](https://docs.maltego.com/support/solutions/articles/15000017605-writing-local-transforms-in-python)

Transforms written using this library can be used as either local or server transforms.

To run a local transform from your project, you will need to pass the following arguments:

``` bash
project.py local <transform_name>
```

You can find the correct transform_name to use by running `python project.py list`.

### Caveats

The following values are not passed to local transforms, and will have dummy values in their place:

- `type`: `local.Unknown`
- `weight`: 100
- `slider`: 100
- `transformSettings`: {}

## Using the Transform Registry

###### Added in 1.4.0 (July 2021)

The Transform Registry enables you to annotate Transforms with metadata like display name, description, input and output
entities as well as settings. The Transform Registry will automatically generate CSV files that you can import into the
pTDS and/or your iTDS.

### Configuring the Registry

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

### Annotating Transforms

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

### Transform Settings

You can declare transform settings in a central location and add them to the registry.

#### Configuring Global Settings

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

### Generating an `.mtz` config with your local Transforms

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

## Legacy Transforms

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

## CLI

The following commands can be run using the project.py file.

### Run Server

``` bash
python project.py runserver
```

Start a development server that you can use to develop new transforms.

### List

``` bash
python project.py list
```

List the available transforms together with their transform server URLs and local transform names.

## Reference

### Constants

The following constants can be imported from `maltego_trx.maltego`.

**Message Types:**

- `UIM_FATAL`
- `UIM_PARTIAL`
- `UIM_INFORM`
- `UIM_DEBUG`

**Please take note:**
You need to enable the `debug` filter option in the Desktop client Output window to view `debug` transform messages.

**Bookmark Colors:**

- `BOOKMARK_COLOR_NONE`
- `BOOKMARK_COLOR_BLUE`
- `BOOKMARK_COLOR_GREEN`
- `BOOKMARK_COLOR_YELLOW`
- `BOOKMARK_COLOR_PURPLE`
- `BOOKMARK_COLOR_RED`

**Link Styles:**

- `LINK_STYLE_NORMAL`
- `LINK_STYLE_DASHED`
- `LINK_STYLE_DOTTED`
- `LINK_STYLE_DASHDOT`

### Enums

**Overlays:**

Overlays Enums are imported from `maltego_trx.overlays`

*Overlay OverlayPosition:*

- `NORTH = "N"`
- `SOUTH = "S"`
- `WEST = "W"`
- `NORTH_WEST = "NW"`
- `SOUTH_WEST = "SW"`
- `CENTER = "C"`

*Overlay Type*

- `IMAGE = "image"`
- `COLOUR = "colour"`
- `TEXT = "text"`

### Request/MaltegoMsg

The request/maltego msg object given to the transform contains the information about the input entity.

**Attributes:**

- `Value: str`: The display value of the input entity on the graph
- `Weight: int`: The weight of the input entity
- `Slider: int`: Results slider setting in the client
- `Type: str`: The input entity type
- `Properties: dict(str: str)`: A key-value dictionary of the input entity properties
- `TransformSettings: dict(str: str)`: A key-value dictionary of the transform settings
- `Genealogy: list(dict(str: str))`: A key-value dictionary of the Entity genealogy, this is only applicable for
  extended entities e.g. Website Entity

**Methods:**

- `getProperty(name: str)`: Get a property value of the input entity
- `getTransformSetting(name: str)`: Get a transform setting value
- `clearLegacyProperties()`: Delete (duplicate) legacy properties from the input entity. This will not result in
  property information being lost, it will simply clear out some properties that the TRX library duplicates on all
  incoming Transform requests. In older versions of TRX, these Entity properties would have a different internal ID when
  sent the server than what the Maltego client would advertise in the Entity Manager UI. For a list of Entities with
  such properties and their corresponding legacy and actual IDs, see `entity_property_map` in `maltego_trx/entities.py`.
  For the majority of projects this distinction can be safely ignored.

### Response/MaltegoTransform

**Methods:**

- `addEntity(type: str, value: str) -> Entity`: Add an entity to the transform response. Returns an Entity object
  created by the method.
- `addUIMessage(message: str, messageType='Inform')`: Return a UI message to the user. For message type, use a message
  type constant.

### Entity

**Methods:**

- `setType(type: str)`: Set the entity type (e.g. "Phrase" for maltego.Phrase entity)
- `setValue(value: str)`: Set the entity value
- `setWeight(weight: int)`: Set the entity weight
- `addDisplayInformation(content: str, title: str)`: Add display information for the entity.
- `addProperty(fieldName: str, displayName: str, matchingRule: str, value: str)`: Add a property to the entity. Matching
  rule can be `strict` or `loose`.
- `addOverlay(propertyName: str, position: OverlayPosition, overlay_type: OverlayType)`: Add an overlay to the entity.
  `OverlayPosition` and `OverlayType` are defined in the `maltego_trx.overlays`

Overlay can be added as Text, Image or Color

```python 
        
        person_name = request.Value
        entity = response.addEntity(Phrase, "Hi %s, nice to meet you!" % person_name)

        # Normally, when we create an overlay, we would reference a property name so that Maltego can then use the
        # value of that property to create the overlay. Sometimes that means creating a dynamic property, but usually
        # it's better to either use an existing property, or, if you created the Entity yourself, and only need the
        # property for the overlay, to use a hidden property. Here's an example of using a dynamic property:
        entity.addProperty(
            'dynamic_overlay_icon_name', 
            displayName="Name for overlay image", 
            value="Champion"  # references an icon in the Maltego client
        )
        entity.addOverlay('dynamic_overlay_icon_name', OverlayPosition.WEST, OverlayType.IMAGE)

        # DISCOURAGED:
        # You *can* also directly supply the string value of the property, however this is not recommended. Why? If
        # the entity already has a property of the same ID (in this case, "DE"), then you would in fact be assigning the
        # value of that property, not the string "DE", which is not the intention. Nevertheless, here's an example:
        entity.addOverlay(
            'DE', # name of an icon, however, could also accidentally be a property name
            OverlayPosition.SOUTH_WEST, 
            OverlayType.IMAGE
        )

        # Overlays can also be used to display extra text on an entity:
        entity.addProperty("exampleDynamicPropertyName", "Example Dynamic Property", "loose", "Maltego Overlay Testing")
        entity.addOverlay('exampleDynamicPropertyName', OverlayPosition.NORTH, OverlayType.TEXT)

        # Or a small color indicator:
        entity.addOverlay('#45e06f', OverlayPosition.NORTH_WEST, OverlayType.COLOUR)
```

- `setIconURL(url: str)`: Set the entity icon URL
- `setBookmark(bookmark: int)`: Set bookmark color index (e.g. -1 for BOOKMARK_COLOR_NONE, 3 for BOOKMARK_COLOR_PURPLE)
- `setNote(note: str)`: Set note content
- `setGenealogy(genealogy: dict)`: Set genealogy

**Link Methods:**

- `setLinkColor(color: str)`: Set the link color (e.g. hex "#0000FF" for blue)
- `setLinkStyle(style: int)`: Set the link style index (e.g. 0 for LINK_STYLE_NORMAL, 2 for LINK_STYLE_DOTTED)
- `setLinkThickness(thick: int)`: Set link thickness (default is 1)
- `setLinkLabel(label: str)`: Set the label of the link
- `reverseLink()`: Reverse the link direction
- `addCustomLinkProperty(fieldName=None, displayName=None, value=None)`: Set a custom property for the link
