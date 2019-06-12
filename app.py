"""
getDomainAge() is a simple web-based job scheduler application developed in python using flask micro framework and SQLAlchemy as ORM to get the age of a domain in days
This application is to showcase the scrapping and web capability of python. The domain informations are scrapped from https://www.whois.com/

Author: Lakhya Jyoti Nath (ljnath)
Email:  ljnath@ljnath.com
Website: https://www.ljnath.com
"""


from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory, get_flashed_messages
from wtforms import Form, StringField, TextAreaField, validators
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from bs4 import BeautifulSoup

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import sys
import traceback
import os
import re
import pickle
import time
import smtplib
import csv
import requests
import logging.handlers
from enum import Enum
from datetime import datetime, timedelta, date
from subprocess import threading
from urllib.parse import urlparse


__version__ = 0.1
__author__ ='Lakhya Jyoti Nath'
__name__ = 'getDomainAge'


WHOIS_URL = 'https://www.whois.com/whois/'              # remote URL for fetching domain infomation
DEFAULT_AGE = 0                                         # default age of domain
REGISTERED_DATE_FORMAT = '%Y-%m-%d'                     # date format of the domain registration date
DOMAIN_CACHE = {}                                       # for caching results
JOBS_CACHE = None                                       # for maintaining job cache
MIN_WAIT_TIME_BETWEEN_JOBS = 2                          # in seconds
MAX_WAIT_TIME_BETWEEN_JOBS = 120                        # in seconds
SESSION_TIMEOUT = 10                                    # in minutes
JOBS_PER_PAGE = 10                                      # number of job to be displayed in each UI page
SECRET_KEY = 'developed-by-ljnath'

APP_PATH = os.path.dirname(os.path.abspath(__file__))   # path where this application is placed

DB_FILE_PATH = "{}/domain.db".format(APP_PATH)          # database file path
CACHE_FILE_PATH = "{}/domain.cache".format(APP_PATH)    # cache file path
RESULTS_DIRECTORY =  "{}/results".format(APP_PATH)      # result directory path
LOG_DIRECTORY =  "{}/logs".format(APP_PATH)             # log directory path

os.makedirs(LOG_DIRECTORY, exist_ok=True)               # creating the log directory if it is missing

LOG_HANDLER = logging.handlers.RotatingFileHandler('{}/app.log'.format(LOG_DIRECTORY), maxBytes=1024 * 1024 * 10)                           # log handler with size-based rotation
LOG_HANDLER.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))# log message format

SMTP_HOST = 'smtp.server'                               # SMTP hostname for email
SMTP_PORT = 587                                         # SMTP port for email
SMTP_USERNAME = ''                                      # Username for your SMTP server (Optional)
SMTP_PASSWORD = ''                                      # Password for yout SMTP server (Optional)
SENDER_EMAIL = 'get-domain-age@ljnath.com'              # sender email which will be used for sending email

APP_HOST = '0.0.0.0'                                    # host name where this application will be running
APP_PORT = 5000                                         # port number on which this application will be running
APP_DEBUG_MODE = False                                  # start application in debug mode


app = Flask(__name__)                                                           # creating flask application
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(DB_FILE_PATH)     # application configuration for adding DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Status(Enum):
    """
    Enum for job status
    """
    RUNNING = 'RUNNING'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    
class DomainChecker():
    """ 
    Class for getting domain information
    """
    def __init__(self):
        self.__logger = logging.getLogger('domain-checker')
        self.__logger.setLevel(logging.INFO)
        self.__logger.addHandler(LOG_HANDLER)
        if not self.__logger.hasHandlers():
            self.__logger.addHandler(LOG_HANDLER)

    def __cache_lookup(self, domain_name:str):
        """ Checks for existing result for a given domain name
            :pram domain_name : domain_name in string which needs to be checked in the local cache
            :return : returns the domain registrated date for a given domain
        """
        return DOMAIN_CACHE[domain_name] if domain_name in DOMAIN_CACHE.keys() else date.today()

    def __save_cache(self):
        """ Saves the cache to disk """
        with open(CACHE_FILE_PATH, 'wb') as file_handler:
            pickle.dump(DOMAIN_CACHE, file_handler)

    def __get_domain_from_url(self, url:str):
        """ Gets the domain name from a given URL using urlparser
            :param : url in string for which the domain name has to be extracted
            :return : returns the domain name
        """
        domain_name = None
        try:
            domain_name = '{uri.netloc}'.format(uri=urlparse(url))
        except:
            domain_name = None
            self.__logger.warning('Failed to parse domain name from URL {}'.format(url))
        finally:
            return domain_name

    def __get_domain_age(self, registered_date:str):
        """ Method to get the age of domain from its registration date
            :param registered_date : registered_date as string is the registration date of the domain
            :return age : age as integer is the age in days
        """
        date_of_registration = datetime.strptime(registered_date, REGISTERED_DATE_FORMAT)
        delta =  datetime.today() - date_of_registration
        return delta.days

    def get_registered_date(self, urls:list):
        """ Fetches and returns registration date for each domain in the list of URLs
        :param domains : list of domains which needs to be processed
        :return : returns list of sets with domain and its registration date
        """
        global DOMAIN_CACHE
        results = []
        for url in urls:
            domain_age = DEFAULT_AGE
            domain_name = self.__get_domain_from_url(url)
            
            # validation check
            if not domain_name:
                results.append((url, 'NA', domain_age))
                self.__logger.warn('Invalid input URL {}'.format(url))
                continue                

            # performing cache lookup
            registration_date = self.__cache_lookup(domain_name)
            if registration_date != date.today():
                results.append((url, domain_name, self.__get_domain_age(registration_date)))
                self.__logger.info('Registration date found in local cache. Domain {} was registered on {}, it is {} day() old'.format(domain_name, registration_date, self.__get_domain_age(registration_date)))
                continue

            # extracting registration date of domain from remote site
            try:
                response = requests.get('{}/{}'.format(WHOIS_URL, domain_name))
                if response.status_code != 200:
                    self.__logger.error('Received invalid response from remote URL {}. Expected 200, received {}'.format(WHOIS_URL, response.status_code))
                else:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    div_blocks = soup.find_all('div', attrs={'class': 'df-block'})
                    if div_blocks and div_blocks[0].find_all('div')[10].text.lower().startswith('registered on'):
                        registration_date = div_blocks[0].find_all('div')[11].text
                domain_age = self.__get_domain_age(registration_date)
                self.__logger.info('Domain information is scrapped from the web. Domain {} was registered on {}, it is {} day(s) old'.format(domain_name, registration_date, domain_age))
                results.append((url, domain_name, domain_age))
                DOMAIN_CACHE.update({domain_name : registration_date})
            except Exception as e:
                self.__logger.exception(e, exc_info=True)
                results.append((url, domain_name, domain_age))

        self.__save_cache()
        return results

class Worker():
    """
    Worker class for handling jobs and processing those
    """
    def __init__(self):
        self.__logger = logging.getLogger('worker')
        self.__logger.setLevel(logging.INFO)
        self.__logger.addHandler(LOG_HANDLER)
        if not self.__logger.hasHandlers():
            self.__logger.addHandler(LOG_HANDLER)
        os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
        self.__logger.info('Created a new worker')
            
    def __save_result(self, job_id, results):
        """ Method to save domain results to CSV file
            :param : job_id as integer whose results have to be saved
            :param : results as list of sets containing URL and its registration date
        """
        output_result_file  = '{}/job_id_{}.csv'.format(RESULTS_DIRECTORY, job_id)
        with open(output_result_file, "w", encoding='utf-8', newline='') as file_handler:
            csvWriter = csv.writer(file_handler)
            csvWriter.writerow(['URL', 'Domain Name', 'Age (in days)'])
            [csvWriter.writerow([result[0], result[1], result[2]]) for result in results]
            self.__logger.info('Job #{}: Saved {} results to file {}'.format(job_id, len(results), output_result_file))
        return output_result_file

    def __update_status(self, job_id, status:Status):
        """ Method to update the job status in the database
            :param job_id : job_id as integer which status needs to be updated
            :param status : staus as Status, the new status of the job
        """
        job_record = Job.query.filter_by(job_id=job_id).first()
        current_status = job_record.status
        job_record.status = status.value
        if status == Status.COMPLETED:
            job_record.completed_on = datetime.now()
        db.session.flush()
        db.session.commit()
        requests.post('http://localhost:{}/{}/update-job-cache'.format(APP_PORT, __name__), headers={'API_KEY' : SECRET_KEY})
        self.__logger.info('Job #{}: updated job status from {} to {} and updated job-cache'.format(job_id, current_status, status.value))

    def __send_email(self, job_id, receiver_email, result_file):
        """ Method to notify the job requester via email
            :param job_id : job_id as integer whose results needs to be emailed
            :param receiver_email : receiver_email as string who is suppose to receive the email
            :param result_file : result_file as string is the filepath to the CSV result file which will be attached with the email
        """
        try:
            html_message = '<html><head><title>getDomainAge() - Results</title></head><body>Hello User,<br>Thank you for using getDomainAge(), please find the age in days for your requested domain name(s) in the attached file.<br><br>-Cheers!<br>getDomainAge()'
            email_message = MIMEMultipart('alternative')
            email_message['To']  = receiver_email
            email_message['From'] = 'operatieve@tovarsales70.ru'
            email_message['Subject'] = "getDomainAge() - result of job #{}".format(job_id)
            email_message.attach(MIMEText(html_message, 'html'))
            if os.path.exists(result_file):
                with open(result_file, "rb") as file_handler:
                    attachment_part = MIMEBase('application', 'octet-stream')
                    attachment_part.set_payload(file_handler.read())
                    encoders.encode_base64(attachment_part)
                    attachment_part.add_header('Content-Disposition', "attachment; filename= {}".format(os.path.basename(result_file)))
                    email_message.attach(attachment_part)
            smtp_server  = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
            smtp_server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp_server.sendmail(email_message['From'], email_message['To'], email_message.as_string())
            smtp_server.quit()
            self.__logger.info('Job #{}: Successfully emailed results "{}" to {} '.format(job_id, os.path.basename(result_file), receiver_email))
        except Exception as e:
            self.__logger.exception(e, exc_info=True)
            self.__logger.error('Job #{}: Failed to email results "{}" to {}'.format(job_id, os.path.basename(result_file), receiver_email))

    def run(self):
        """ Method to check database for new job at an interval and process those jobs
        """
        self.__logger.info('Worker is runnnig with an minimum and maximum interval of {} and {} seconds respectively'.format(MIN_WAIT_TIME_BETWEEN_JOBS, MAX_WAIT_TIME_BETWEEN_JOBS))
        is_worker_busy = False
        while True:
            new_job = Job.query.filter_by(status=Status.PENDING.value).first()
            wait_time = MIN_WAIT_TIME_BETWEEN_JOBS if new_job else MAX_WAIT_TIME_BETWEEN_JOBS
            if new_job and not is_worker_busy:
                is_worker_busy = True
                self.__logger.info('Job #{}: Starting to work on it'.format(new_job.job_id))
                self.__update_status(new_job.job_id, Status.RUNNING)
                domain_checker = DomainChecker()
                results = domain_checker.get_registered_date(new_job.urls.split(','))
                self.__send_email(new_job.job_id, new_job.requested_by, self.__save_result(new_job.job_id, results))
                self.__update_status(new_job.job_id, Status.COMPLETED)
                self.__logger.info('Job #{}: Completed job'.format(new_job.job_id))
                is_worker_busy = False
            time.sleep(wait_time)

class Job(db.Model):
    """
    Representation of Job table in the database
    """
    __tableName__ = 'Users'
    job_id = db.Column('job_id', db.Integer, primary_key=True)
    requested_by = db.Column('requested_by', db.String(50), nullable=False)
    requested_on = db.Column('requested_on', db.DateTime(), nullable=False)
    status = db.Column('status', db.String(10), nullable=False)
    urls = db.Column('urls', db.String(99999), nullable=False)
    completed_on = db.Column('completed_on', db.DateTime(), nullable=True)

    def __init__(self, requested_by, requested_on, status, urls):
        self.requested_by = requested_by
        self.requested_on = requested_on
        self.status = status
        self.urls = urls

class AddJobForm(Form):
    """
    Add new job form 
    """
    urls = TextAreaField('URLs (comma or newline seperated)', [validators.Length(min=1, max=99999)], render_kw={"rows": 25})



"""
Flask application code starts from here
"""


def initialize_database():
    """ Method to create and initialize the database
    """
    db.create_all()
    app.logger.info('Successfully created and initialized database')

def get_prev_next_page_number(max_page, current_page):
    """ To calculate the previous and next page number for the pagination system, maximum number of page number shown is 3
        :max_page : max_page as integer is the maximum number of available pages
        :current_page : current_page as integer is the current page number
        :return previous_page, next_page : previous and next page numbers as integers
    """
    previous_page, next_page = 1, max_page
    if current_page == previous_page:       # if first page is selected, then the previous page number is 1
        previous_page = 1
    elif current_page == max_page:          # if last page is selected, then previous page number is last page - 1 if only 2 pages are there else last page - 3
        previous_page = current_page - 1 if max_page == 2 else 2
    else:
        previous_page = current_page - 1    # previous page is current page - 1 if current page is neither first nor last
        
    if current_page < max_page - 1:         # if next page is possible, then it is set to previous page + 2
        next_page = previous_page + 2
    else:
        next_page = max_page

    return previous_page, next_page

def is_logged_in(f):
    """ Checking if user has already logged in """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not logged it, please login to continue.', 'danger')
            return redirect(url_for(__name__))
    return wrap

@app.route('/', methods=['GET'])
def root():
    """ root end point """
    return redirect(url_for(__name__), code=301)

@app.route('/{}'.format(__name__), methods=['GET', 'POST'])
def getDomainAge():
    """ Application name endpoint """
    session['app_version'] = __version__                    # storing app version in session variable for UI

    if request.method == 'GET' and 'logged_in' in session:  # redirecting to dashboard for GET call and if use have logged in
        session['page_index'] = 2
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':                             # redirecting to index page for GET call and if use have not logged in
        return render_template('index.html')

    if request.method == 'POST':                            # performing login operation for POST call and redirecting to dashboard
        user_email = request.form['email'].lower()
        if user_email and re.fullmatch(r'[^@]+@[^@]+\.[^@]+', user_email, re.I):
            session['logged_in'] = True
            session['view_all'] = False
            session['email'] = user_email
            app.logger.info('User {} has logged in'.format(user_email))
            return redirect(url_for('dashboard'))
        else:
            app.logger.warn('Entered email {} is invalid'.format(user_email))
            return render_template('index.html', error='Invalid email ID. Please enter correct ID.')
        
@app.route('/{}/dashboard'.format(__name__))
@is_logged_in
def dashboard():
    """ dashboard endpoint which displays the application dashboard """
    if not JOBS_CACHE:
        requests.post('http://localhost:{}/{}/update-job-cache'.format(APP_PORT, __name__), headers={'API_KEY' : SECRET_KEY})
        app.logger.info('Updated job cache as job cache is empty')

    if request.args.get('viewall'):
        session['view_all'] = True if request.args.get('viewall') == 'true' else False
    session['page_index'] = 2 if session['view_all'] else 1

    try:
        page_number = int(request.args.get('page')) if request.args.get('page') else 1
    except:
        page_number = 1

    list_of_jobs = JOBS_CACHE if session['view_all'] else [job for job in JOBS_CACHE if job.requested_by.lower() == session['email']]
    number_of_jobs = len(list_of_jobs)

    max_page = int(number_of_jobs / JOBS_PER_PAGE) + (0 if number_of_jobs % JOBS_PER_PAGE == 0 else 1)
    previous_page, next_page = get_prev_next_page_number(max_page, page_number)
    valid_jobs = list_of_jobs[::-1][JOBS_PER_PAGE * (page_number - 1):JOBS_PER_PAGE * page_number]
    return render_template('dashboard.html', all_jobs=valid_jobs, page=page_number, last=max_page, start=previous_page, end=next_page)

@app.route('/{}/download/<filename>'.format(__name__), methods=['GET'])
@is_logged_in
def download(filename):
    """ download endpoint for directly downloading the result file """
    job_id = filename.strip().split('.')[0]
    if not job_id or not re.match(r'[\d]', job_id):                                                             # for no of invalid job id
        flash('You have made an invalid request.', 'danger')
        return redirect(url_for(__name__))
        
    job_record = Job.query.filter_by(job_id=job_id).first()
    if job_record and job_record.requested_by == session['email']:                                              # if job id was created by this same email
        if not os.path.exists('{}/job_id_{}.csv'.format(RESULTS_DIRECTORY, job_id)):
            flash('The file you are looking for {}.csv is missing.'.format(job_id), 'warning')
            return redirect(url_for(__name__))
        return send_from_directory(directory=RESULTS_DIRECTORY, filename='job_id_{}.csv'.format(job_id))
    else:                                                                                                       # if job id was not created by this same email
        flash('You do not have permission to download this file as you are not the owner of it.', 'danger')
        return redirect(url_for(__name__))

@app.route('/{}/job'.format(__name__), methods=['GET', 'POST'])
@is_logged_in
def job():
    """ job endpoint for placing new job request """
    session['page_index'] = 0
    form = AddJobForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            all_urls = [id.replace('\n','').strip() for id in form.urls.data.strip().split('\n')]
            updated_urls = []
            for url in all_urls:
                if ',' in url:
                    updated_urls += [temp_id.strip() for temp_id in url.split(',')]
                else:
                    updated_urls.append(url)

            data_pair = Job(requested_by=session['email'], requested_on = datetime.now(), status = Status.PENDING.value, urls=','.join(updated_urls))
            db.session.add(data_pair)
            db.session.commit()
            flash('Your job has been added, please wait for it to be processed', 'success')
            app.logger.info('User {} has added a new job'.format(session['email']))
            requests.post('http://localhost:{}/{}/update-job-cache'.format(APP_PORT, __name__), headers={'API_KEY' : SECRET_KEY})
            app.logger.info('Updated job cache as a new job has been added')
        except sqlite3.OperationalError:
            flash('Failed to add your job because of a database error. Please try again', 'failed')
            app.logger.error('Failed to add job because of database error')
        return redirect(url_for('dashboard'))
    return render_template('job.html', form=form)

@app.route('/{}/logout'.format(__name__))
@is_logged_in
def logout():
    """ logout endpoint for user to logout """
    temp_email = session['email']
    session.clear()
    flash('You have successfuly logged out', 'success')
    app.logger.info('User {} has logged out'.format(temp_email))
    return redirect(url_for(__name__))


@app.route('/{}/update-job-cache'.format(__name__), methods=['POST'])
def reload_job(force = False):
    """ Method to update the local job cache
        :param : force as boolean if the cache update needs to be forcefully done
    """
    global JOBS_CACHE
    if request.method == 'POST' and request.headers['API_KEY'] == SECRET_KEY:
        JOBS_CACHE = Job.query.all()
    return ''

@app.errorhandler(404)
def error_page(e):
    """ Handling 404 error """
    session['app_version'] = __version__
    return render_template('error.html', code=404, message='Congratulation! You have discovered this secret page.')


if __name__ == 'getDomainAge':
    try:
        # configuring application logging
        logging.getLogger('werkzeug').setLevel(logging.DEBUG)
        logging.getLogger('werkzeug').addHandler(LOG_HANDLER)
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(LOG_HANDLER)
        if not app.logger.hasHandlers():
            app.logger.addHandler(LOG_HANDLER)

        app.logger.info('Starting application getDomainAge v{}'.format(__version__))

        # configuring database in case it does not exist
        if not os.path.exists(DB_FILE_PATH):
            app.logger.info('Database file is missing, initializing it now')
            initialize_database()

        # loading cache file is found
        if os.path.exists(CACHE_FILE_PATH):
            app.logger.info('Detected existing cache file, loading it now')
            with open(CACHE_FILE_PATH, 'rb') as file_handler:
                DOMAIN_CACHE = pickle.load(file_handler)
                app.logger.info('Successfully loaded {} records from cache file'.format(len(DOMAIN_CACHE.keys())))

        # creating and starting worker a seperate thread
        app.logger.info('Creating worker thread')
        worker = Worker()
        worker_thread = threading.Thread(target=worker.run)
        worker_thread.start()

        # starting flask web application 
        app.logger.info('Starting web server')
        app.permanent_session_lifetime = timedelta(minutes=30)
        app.secret_key=SECRET_KEY
        app.run(debug=APP_DEBUG_MODE, host=APP_HOST, port=APP_PORT, threaded=True)
    except:
        self.__logger
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        
    
