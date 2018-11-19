FROM ubuntu:16.04

RUN mkdir /var/www/
RUN mkdir /var/www/TRX/
WORKDIR /var/www/TRX/

# Install apache2 for production server
RUN apt-get update
RUN apt-get install apache2 -y
RUN apt-get install libapache2-mod-wsgi -y
RUN apt-get install python-pip -y

COPY ./TRX.conf /etc/apache2/sites-available/TRX.conf
RUN a2ensite TRX.conf
RUN echo "Listen 8080" >> /etc/apache2/ports.conf

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /var/www/TRX/

RUN chown -R www-data:www-data /var/www/TRX/

CMD ["python", "project.py", "runserver"]
