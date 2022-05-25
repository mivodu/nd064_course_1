FROM python:3.8
LABEL maintainer="Michael Volkmann"

COPY . /app
WORKDIR /app
RUN pip install -r /solutions/python-helloworld/requirements.txt

# command to run on container start
CMD [ "python", "app.py" ]
