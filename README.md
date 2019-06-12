# getDomainAge
### Version : 0.1

Author : Lakhya Jyoti Nath (ljnath)
Email : ljnath@ljnath.com
Website : https://www.ljnath.com

Date : June 2019

## What is it ?
getDomainAge is a simple web-based job scheduler application developed in python using flask micro framework and SQLAlchemy as ORM to get the age of a domain in days.<br>
This application is to showcase the scrapping and web capability of python. The domain informations are scrapped from https://www.whois.com/


## How to works ?
- It works by scrapping the domain registration date from https://www.whois.com/
- User places their job request using the web portal where they can enter onr or more URLs in comma or new-line seperated manner. Jobs are stored in SQLite DB
- A scheduler keeps on running every 2 or 120 seconds (configurable). It checks the DB for any new job and processes it.
- For every job, an instance of 'Domain Checker' class is created. It gives the domain registration date from its local cache if available else it gets from https://www.whois.com.
- The result is cached if it is not present in the cache system
- Results is saved as CSV file and mailed to the user who had requested the job

## How to use ?
- Login with your email ID
- Add a new job where you need to enter your list of URLs in a form, which can be comma or new-line seperated
- Wait for your job to be processed. Once processed, you will receive an email with the zcodes.

