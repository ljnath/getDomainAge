from datetime import timedelta

from flask import Flask

from getDomainAge.handlers.config import ConfigHandler
from getDomainAge.handlers.environment import Environment

app = Flask(__name__)


class GetDomainAge:
    def __init__(self, config_file):
        config_handler = ConfigHandler(config_file)
        app_configuration = config_handler.load()
        Environment().initialize(app_configuration)

    def run(self):
        env = Environment()

        import getDomainAge.controllers.app
        from getDomainAge.services.database import DatabaseService

        database_service = DatabaseService()
        database_service.initialize()

        # starting flask web application
        app.logger.info('Starting web server')
        app.permanent_session_lifetime = timedelta(minutes=30)
        app.secret_key = env.api_secrect_key

        app.run(env.server_host, env.server_port, threaded=True, debug=env.server_debug_mode)
