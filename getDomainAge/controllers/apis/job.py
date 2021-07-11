from flask import redirect, render_template, request, session, url_for
from getDomainAge import app
from getDomainAge.controllers import has_logged_in
from getDomainAge.handlers.environment import Environment
from getDomainAge.models.enums import (Endpoint, HttpMethod, RequestParam,
                                       SessionParam, SiteLink, Template)
from getDomainAge.models.forms.add_job import AddJobForm
from getDomainAge.services.job import JobService
from getDomainAge.services.notification import NotificationService
from getDomainAge.services.ui import UIService

notification_service = NotificationService()
job_service = JobService()
env = Environment()


@app.route(f'/{Endpoint.API_JOB_VIEW.value}', methods=[HttpMethod.GET.value])
@has_logged_in
def api_add_view():
    """
    endpoint: /getDomainAge/api/job/view
    job endpoint for placing new job request
    """
    job_service.update_job_cache()

    session[SessionParam.VIEW_ALL.value] = False if request.args.get(RequestParam.ALL.value) is None else True
    session[SessionParam.PAGE_INDEX.value] = 2 if session[SessionParam.VIEW_ALL.value] else 1

    try:
        page_number = int(request.args.get(RequestParam.PAGE.value)) if request.args.get(RequestParam.PAGE.value) else 1
    except ValueError:
        page_number = 1

    jobs_to_view = env.cached_jobs if session[SessionParam.VIEW_ALL.value] else [job for job in env.cached_jobs if job.requested_by.lower() == session[SessionParam.EMAIL.value]]
    number_of_jobs = len(jobs_to_view)

    max_page = int(number_of_jobs / env.app_job_per_page) + (0 if number_of_jobs % env.app_job_per_page == 0 else 1)
    previous_page, next_page = UIService().get_prev_next_page_number(max_page, page_number)

    valid_jobs = jobs_to_view[::-1][env.app_job_per_page * (page_number - 1):env.app_job_per_page * page_number]

    return render_template(Template.DASHBOARD.value, all_jobs=valid_jobs, page=page_number, last=max_page, start=previous_page, end=next_page)


@app.route(f'/{Endpoint.API_JOB_ADD.value}', methods=[HttpMethod.POST.value])
@has_logged_in
def api_add_job():
    """
    endpoint: /getDomainAge/api/job/add
    job endpoint for placing new job request
    """
    add_job_form = AddJobForm(request.form)

    if request.method == HttpMethod.POST.value and add_job_form.validate():
        updated_urls = []

        # splitting URLs if user has used new lines
        parsed_urls = [id.replace('\n', '').strip() for id in add_job_form.urls.data.strip().split('\n')]

        # splitting URLs if user has used comma
        for url in parsed_urls:
            if ',' in url:
                updated_urls += [temp_id.strip() for temp_id in url.split(',')]
            else:
                updated_urls.append(url)

        if job_service.add_new_job(updated_urls, session[SessionParam.EMAIL.value]):
            notification_service.notify_success('Your job has been added, please wait for it to be processed.')
        else:
            notification_service.notify_failure('Failed to added new job, please try aftersome.')

        return redirect(url_for(SiteLink.DASHBOARD.value))

    return render_template(Template.JOB.value, form=add_job_form)


# @app.route(f'/{Endpoint.DOWNLOAD.value}/<filename>', methods=[HttpMethod.GET.value])
# @has_logged_in
# def download(filename):
#     """
#     endpoint: /getDomainAge/download/<filename>
#     download endpoint for directly downloading the result file
#     """
#     # if filename is empty of filename is not in the form filename.ext
#     try:
#         job_id = filename.strip().split('.')[0]
#     except Exception:
#         notification_service.notify_error('Invalid filename.')
#         return redirect(url_for(SiteLink.HOMEPAGE.value))

#     # if filename is not a digit and contains some other character
#     if not job_id or not re.match(r'[\d]', job_id):
#         notification_service.notify_error('You have made an invalid request.')
#         return redirect(url_for(SiteLink.HOMEPAGE.value))

#     # fetching job record by job_id
#     job_record = db_service.get_job(job_id)

#     # checking if job_record is found and if the job was requested by the logged-in user
#     if job_record and job_record.requested_by == session[SessionParam.EMAIL.value]:

#         # if file is missing, notifying user
#         if not os.path.exists(f'{env.result_directory}/job_id_{job_id}.csv'):
#             notification_service.notify_warning('The result {}.csv that you are looking for is missing.'.format(job_id))
#             return redirect(url_for(SiteLink.HOMEPAGE.value))

#         # if file is present, starting the download
#         return send_from_directory(directory=env.result_directory, filename=f'job_id_{job_id}.csv')
#     else:
#         # if job id was not created by this same email, showing warning message
#         notification_service.notify_error('You do not have permission to download this file as you did not place the job.')
#         return redirect(url_for(SiteLink.HOMEPAGE.value))
