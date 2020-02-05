# Written by ljnath (www.ljnath.com) | Feb 5th, 2020

# pull the python3 based alpine linux
FROM frolvlad/alpine-python3

# configure the working directory for the getDomainAge application
WORKDIR /usr/src/app

# copy all the required file and folders needed to run the application
COPY requirements.txt ./
COPY app.py app.py
COPY templates templates

# install all python dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# run the getDomainAge application
CMD [ "python", "./app.py" ]