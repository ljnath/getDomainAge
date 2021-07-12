from wtforms import Form, TextAreaField, validators


class AddJobForm(Form):
    """
    Class for creating new FOrm for user to enter URLs
    """

    urls = TextAreaField('URLs (comma or newline seperated)', [validators.Length(min=1, max=99999)], render_kw={"rows": 20})
