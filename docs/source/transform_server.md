# Transform Server

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
