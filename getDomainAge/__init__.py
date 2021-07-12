import threading
from datetime import timedelta

from flask import Flask

from getDomainAge.handlers.config import ConfigHandler
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler

app = Flask(__name__)


class GetDomainAge:
    def __init__(self, config_file):
        config_handler = ConfigHandler(config_file)
        app_configuration = config_handler.load()
        Environment().initialize(app_configuration)

    def run(self):
        env = Environment()
        
        app.logger = LogHandler.get_logger('werkzeug', env.log_path)
        

        import getDomainAge.controllers.app
        from getDomainAge.handlers.cache.domain import DomainCacheHandler
        from getDomainAge.services.database import DatabaseService
        from getDomainAge.services.worker import WorkerService

        DomainCacheHandler().load_from_disk()
        DatabaseService().initialize()

        # creating and starting worker a seperate thread
        app.logger.info('Creating worker thread, starting with an initial delay of 5')
        worker_service = WorkerService()
        worker_thread = threading.Thread(target=worker_service.run)
        worker_thread.start()

        # starting flask web application
        app.logger.info('Starting web server')
        app.permanent_session_lifetime = timedelta(minutes=env.app_session_timeout)
        app.secret_key = env.api_secrect_key

        app.run(env.server_host, env.server_port, threaded=True, debug=env.server_debug_mode)
