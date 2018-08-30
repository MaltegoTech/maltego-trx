# Maltego TRX Python Library

## Getting Started
The library can be used in either Python2 or Python 3.

To install the trx library run the following command:
```
pip install maltego-trx
```

After installing you can create a new project by running the following command:
```
maltego-trx start new_project
```

This will create a folder new_project with the recommend project structure.

**Adding a Transform:**

Add a new transform by creating a new python file in the "transforms" folder of your directory.

Any file in the folder where the **class name matches the filename** and the class inherits from Transform, will automatically be discovered and added to your server.


A simple transform would look like the following:

`new_project/transforms/GreetPerson.py`
```python
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

**Running the development server:**

You can start the development server, by running the following command:
```
python server.py
```

This will startup a development server that automatically reloads every time the code is changed.

## Demo Project
The demo folder provides an example project. The Docker files given can be used to setup and run your project in Docker.

The Dockerfile and docker-compose file can be used to easily setup and run a development transform server.

If you have copied the `docker-compose.yml`, `Dockerfile` and `prod.yml` files into your project, 
then you can use the following commands to run the server in Docker.

Run the following to start the development server:
```
docker-compose up
```

Run the following command to run a production gunicorn server:
```
docker-compose -f prod.yml up --build
```

For publicly accessible servers, it is recommended to run your Gunicorn server behind proxy servers such as Nginx.

## Legacy Transforms
If you have old TRX transforms that are written as functions, 
they can be registered with the server using the `maltego_trx.registry.register_transform_function` method.

Import the transform function into the `project.py` file in the root directory of your project and call the register method.

`project.py`
```python

from .legacy_transforms import trx_DNS2IP

register_transform_function(trx_DNS2IP)

``` 

You will need to update the Maltego import in your old transform files.

Change:
```python
from Maltego import *
```
To:
```python
from maltego_trx.maltego import *
```