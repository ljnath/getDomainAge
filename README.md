# getDomainAge
### Version : 0.3

Author : Lakhya Jyoti Nath (ljnath)<br>
Date : June 2019 - July 2021<br>
Email : ljnath@ljnath.com<br>
Website : https://www.ljnath.com

[![](https://img.shields.io/docker/pulls/ljnath/getdomainage)](https://hub.docker.com/r/ljnath/getdomainage)
![Docker Image Size (tag)](https://img.shields.io/docker/image-size/ljnath/getdomainage/latest)
[![](https://images.microbadger.com/badges/version/ljnath/getdomainage.svg)](https://microbadger.com/images/ljnath/getdomainage)
[![](https://img.shields.io/github/license/ljnath/getdomainage)](https://github.com/ljnath/getDomainAge)


## What is it ?
getDomainAge is a simple web-based job scheduler application developed in python using flask micro framework and SQLAlchemy as ORM to get the age of a domain in days.<br>
This application is to showcase the scrapping and web capability of python. The domain informations are scrapped from https://www.whois.com/


## How it works ?
- It works by scrapping the domain registration date from https://www.whois.com/
- User places their job request using the web portal where they can enter onr or more URLs in comma or new-line seperated manner. Jobs are stored in SQLite DB
- A scheduler keeps on running every 2 or 120 seconds (configurable). It checks the DB for any new job and processes it.
- For every job, an instance of 'Domain Checker' class is created. It gives the domain registration date from its local cache if available else it gets from https://www.whois.com.
- The result is cached if it is not present in the cache system
- Results is saved as CSV file and mailed to the user who had requested the job

## How to use ?
- Login with your email ID
- Add a new job where you need to enter your list of URLs in a form, which can be comma or new-line seperated
- Wait for your job to be processed. Once processed, you will receive an email with the age of your selected domain.

## How to run using docker ?
To run the getdomainage docker container, run this command
```docker
docker run -p 5000:5000 ljnath/getdomainage
```

In order to run the docker container with existing database and log file, you need to mount the local directory (e.g.: /home/user/getDomainAge) as shown below

```docker
docker run -p 5000:5000 -v /home/user/getDomainAge:/usr/src/app ljnath/getdomainage
```