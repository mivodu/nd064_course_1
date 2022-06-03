# use a Python base image in version 2.7
FROM python:2.7
LABEL maintainer="Michael Volkmann"

# copy application files
COPY ./techtrends /app
WORKDIR /app
# Install packages defined in the requirements.txt file
RUN pip install -U pip wheel setuptools && \\
    pip install -r requirements.txt
# Initialize database
RUN python init_db.py

#Expose the application port 3111
EXPOSE 3111

# command to run on container start to start the application
CMD [ "python", "app.py" ]