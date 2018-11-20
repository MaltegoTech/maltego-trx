FROM ubuntu:18.04

RUN mkdir /var/www/
RUN mkdir /var/www/TRX/
WORKDIR /var/www/TRX/

# System dependencies
RUN apt-get update
RUN apt-get install python3-pip -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Install Gunicorn for running production server
RUN pip3 install gunicorn

COPY . /var/www/TRX/

RUN chown -R www-data:www-data /var/www/TRX/

CMD ["python", "project.py", "runserver"]
