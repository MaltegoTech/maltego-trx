# Getting Started

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

## Adding a Transform

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
