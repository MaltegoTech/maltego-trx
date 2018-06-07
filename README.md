# Maltego Python Transform Library

## Development Setup
### Using Docker
The Dockerfile and docker-compose file can be used to easily setup and run a development transform server.

Run the following to start the development server:
```
docker-compose up
```

### Running directly on your machine
The transform library should work on any machine with Python installed.

With Python 2.7 or 3.5 installed, you will need to install the server dependencies using:
```
pip install -r requirements.txt
```

After installing the required dependencies, start the development server using:
```
python server.py
```

## Writing a Transform
It is recommended that you write your transforms as a class, with one class per file.

This will allow the server to automatically discover transforms that you write.

Future updates to this library will allow transform meta information (name, input type, etc.) to be defined in code.

A simple transform would look like the following:
```python
from libs.entities import Phrase
from libs.transform import DiscoverableTransform


class GreetPerson(DiscoverableTransform):
    """
    Returns a phrase greeting a person on the graph.
    """

    @classmethod
    def create_entities(cls, request, response):
        person_name = request.Value

        response.addEntity(Phrase, "Hi %s, nice to meet you!" % person_name)
```