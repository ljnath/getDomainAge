from flask import render_template, session
from getDomainAge import app
from getDomainAge.handlers.environment import Environment
from getDomainAge.models.enums import SessionParam, Template


@app.errorhandler(404)
def error_404(e):
    """
    Handling 404 error
    """
    session[SessionParam.APP_VERSION.value] = Environment().app_version
    return render_template(Template.ERROR.value, code=404, message='Congratulation! You have discovered this secret page.')
