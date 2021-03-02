# Maltego TRX Python Library

## Getting Started

The library can be used in either Python2 or Python 3 (recommended).

To install the trx library run the following command:

``` bash
pip install maltego-trx
```

After installing you can create a new project by running the following command:

``` bash
maltego-trx start new_project
```

This will create a folder new_project with the recommend project structure.

**Adding a Transform:**

Add a new transform by creating a new python file in the "transforms" folder of your directory.

Any file in the folder where the **class name matches the filename** and the class inherits from Transform, will automatically be discovered and added to your server.

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

This will startup a development server that automatically reloads every time the code is changed.

### For Production

You can run a gunicorn transform server, after installing gunicorn on the host machine and then running the command:

``` bash
gunicorn --bind=0.0.0.0:8080 --threads=25 --workers=2 project:app
```

*For publicly accessible servers, it is recommended to run your Gunicorn server behind proxy servers such as Nginx.*

## Run a Docker Transform server

The `demo` folder provides an example project. The Docker files given can be used to setup and run your project in Docker.

The Dockerfile and docker-compose file can be used to easily setup and run a development transform server.

If you have copied the `docker-compose.yml`, `Dockerfile` and `prod.yml` files into your project, then you can use the following commands to run the server in Docker.

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

## Legacy Transforms

[Documentation](https://docs.maltego.com/support/solutions/articles/15000018299-porting-old-trx-transforms-to-the-latest-version)

If you have old TRX transforms that are written as functions,
they can be registered with the server using the `maltego_trx.registry.register_transform_function` method.

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

*Overlay Position:*
- `NORTH = "N"`
- `NORTH_EAST = "NE"`
- `NORTH_WEST = "NW"`
- `EAST = "E"`
- `CENTER = "C"`
- `WEST = "W"`
- `SOUTH = "S"`
- `SOUTH_EAST = "SE"`
- `SOUTH_WEST = "SW"`

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
- `Genealogy: list(dict(str: str))`: A key-value dictionary of the Entity genealogy, 
    this is only applicable for extended entities e.g. Website Entity

**Methods:**

- `getProperty(name: str)`: get a property value of the input entity
- `getTransformSetting(name: str)`: get a transform setting value

### Response/MaltegoTransform

**Methods:**

- `addEntity(type: str, value: str) -> Entity`: Add an entity to the transform response. Returns an Entity object created by the method.
- `addUIMessage(message: str, messageType='Inform')`: Return a UI message to the user. For message type, use a message type constant.

### Entity

**Methods:**

- `setType(type: str)`: Set the entity type (e.g. "Phrase" for maltego.Phrase entity)
- `setValue(value: str)`: Set the entity value
- `setWeight(weight: int)`: Set the entity weight
- `addDisplayInformation(content: str, title: str)`: Add display information for the entity.
- `addProperty(fieldName: str, displayName: str, matchingRule: str, value: str)`: Add a property to the entity. Matching rule can be `strict` or `loose`.
- `addOverlay(property_name: str, position:Position, overlay_type:OverlayType)`: Add an overlay to the entity. `Position` and `Type` are defined in the `maltego_tx.overlays`

Overlay can be added as Text, Image or Color

```python 
        
        # references the icon name `Champion` from the Maltego Desktop Client and this is will show up as an overlay on the graph
        entity.addOverlay('Champion', Position.EAST, OverlayType.IMAGE)

        # add a dynamic property 
        entity.addProperty("exampleDynamicPropertyName", "Example Dynamic Property", "loose", "Maltego Champion")

        # add the text value of the property `exampleDynamicPropertyName` as an overlay, any existing property name will work
        entity.addOverlay('exampleDynamicPropertyName', Position.NORTH, OverlayType.TEXT)

        # add a color overlay
        entity.addOverlay('#45e06f', Position.NORTH_WEST, OverlayType.COLOUR)

        # add a flag overlay - DE is an icon on the Maltego Desktop Client
        entity.addOverlay('DE', Position.SOUTH_WEST, OverlayType.IMAGE)
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
- `addCustomLinkProperty(fieldname=None, displayName=None, value=None)`: Set a custom property for the link
