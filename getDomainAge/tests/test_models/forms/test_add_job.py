from getDomainAge.models.forms.add_job import AddJobForm
from wtforms import TextAreaField


def test_add_job_form():
    add_job_form = AddJobForm()

    assert isinstance(add_job_form.urls, TextAreaField)
    assert add_job_form.urls.label.text == 'URLs (comma or newline seperated)'
