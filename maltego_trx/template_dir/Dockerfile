FROM python:3.10-slim

RUN apt-get update && apt-get upgrade --yes
RUN apt-get autoremove && apt-get clean

WORKDIR /var/www/maltego-trx/

# Install requirements, Gunicorn, GEvent
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --no-cache-dir --upgrade gunicorn gevent


# Copy project files and assign them to www-data
COPY . .
RUN chown -R www-data:www-data /var/www/maltego-trx/

USER www-data

EXPOSE 8080
ENTRYPOINT ["gunicorn"]
# For ssl, add "--bind=0.0.0.0:8443 --certfile=server.crt --keyfile=server.key"
CMD ["--bind=0.0.0.0:8080", "--workers", "3", "-k", "gevent", "project:application"]