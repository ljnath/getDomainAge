# Written by ljnath (www.ljnath.com) | 5th Feb, 2020
# Updated on 13th July, 2021

# pull the official python docker image
FROM amd64/python:3.9-slim

# creating and configure the working directory for the getDomainAge application
RUN mkdir -p /getDomainAge && mkdir -p /workspace
WORKDIR /getDomainAge

# creating volume for mounting
VOLUME /workspace

# parameterized the CONFIG-FILE nmae
ARG CONFIG_FILE
ENV CONFIG_FILE=${CONFIG_FILE}

# copy all the required file and folders needed to run the application
COPY requirements.txt runserver.py ./
COPY getDomainAge getDomainAge

# install all python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# run the getDomainAge application
ENTRYPOINT python /getDomainAge/runserver.py --config "/workspace/${CONFIG_FILE}"