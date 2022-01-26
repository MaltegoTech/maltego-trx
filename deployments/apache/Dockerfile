FROM python:3.9-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade --yes

# Install Apache dependencies
RUN apt-get install --yes apache2 libapache2-mod-wsgi-py3
RUN apt-get autoremove && apt-get clean

# Register and Enable maltego-trx Apache config
COPY maltego-trx.conf /etc/apache2/sites-available/
RUN a2ensite maltego-trx.conf
RUN echo "Listen 8080" >> /etc/apache2/ports.conf

WORKDIR /var/www/maltego-trx/

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy project files and assign them to www-data
COPY . .
# Assert project.wsgi is present
COPY project.wsgi .

RUN chown -R www-data:www-data /var/www/maltego-trx/

EXPOSE 8080
ENTRYPOINT  ["/usr/sbin/apache2ctl"]
CMD ["-D", "FOREGROUND"]