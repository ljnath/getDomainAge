# Written by ljnath (www.ljnath.com) | Feb 5th, 2020
# Updated on 12th July, 2021

# pull the python3 based alpine linux
FROM frolvlad/alpine-python3

LABEL build_version="ljnath/GetDomainAge version: 0.3"

# installing pre-requisites for build pyton pip packages
RUN apk update  && apk add --no-cache build-base python3-dev libffi-dev gcc musl-dev make libevent-dev build-base

# creating and configure the working directory for the getDomainAge application
RUN mkdir -p /getDomainAge && mkdir -p /workspace
WORKDIR /getDomainAge

# creating volume for mounting
VOLUME /workspace

# parameterized the CONFIG-FILE nmae
ARG CONFIG_FILE
ENV CONFIG_FILE=${CONFIG_FILE}

# copy all the required file and folders needed to run the application
COPY requirements.txt ./
COPY runserver.py runserver.py
COPY getDomainAge getDomainAge

# install all python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# run the getDomainAge application
ENTRYPOINT python /getDomainAge/runserver.py --config "/workspace/${CONFIG_FILE}"