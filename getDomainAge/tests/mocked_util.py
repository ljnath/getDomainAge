from datetime import datetime, timedelta
from pathlib import Path

from getDomainAge.handlers.config import ConfigHandler


class MockedUtil:
    def __init__(self):
        pass

    def get_true(self, *arg):
        return True

    def get_false(self, *arg):
        return False

    def get_valid_configs(self, *args):
        valid_json_filepath = f'{Path(__file__).parent.absolute()}/files/valid.json'
        config_handler = ConfigHandler(valid_json_filepath)
        return config_handler.load()

    def get_mocked_age(self, *args):
        return 5
