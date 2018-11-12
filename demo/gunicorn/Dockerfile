FROM python:3

RUN mkdir /code
WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install Gunicorn for running production server
RUN pip install gunicorn

COPY . /code

CMD ["python", "project.py", "runserver"]
