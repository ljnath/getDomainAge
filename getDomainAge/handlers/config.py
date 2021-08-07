import json
import os
from typing import Any, Dict

from getDomainAge.handlers.exception import InvalidInput, MissingConfiguration


class ConfigHandler:
    """
    Class to read and load user configuration from a json file
    """
    def __init__(self, config_file: str):
        self.__config_file = config_file

        if not self.__config_file:
            raise InvalidInput('Input configuation file cannot be empty')

        if not os.path.exists(self.__config_file):
            raise InvalidInput(f'Input configuation file {self.__config_file} is missing')

        if not os.path.isfile(self.__config_file):
            raise InvalidInput(f'Input configuation file {self.__config_file} is not a file')

    def load(self) -> Dict[str, Any]:
        """
        Method to load JSON file.
        :return json_configs : json_configs as dict . All user configuration as a dictionary
        """
        json_configs = {}
        with open(self.__config_file) as json_data_file:
            json_configs = json.load(json_data_file)
        self.__validate(json_configs)
        return json_configs

    def __validate(self, json_configs: Dict[str, Any]) -> None:
        """
        Method to validate if all the expected configuration are present in the input configuration file
        """
        expected_keys = (
            'workspace_path',
            'server',
            ('server', 'host'),
            ('server', 'port'),
            ('server', 'debug'),
            'smtp',
            ('smtp', 'host'),
            ('smtp', 'port'),
            ('smtp', 'username'),
            ('smtp', 'password'),
            ('smtp', 'sender_email'),
            'application',
            ('application', 'jobs_per_page'),
            ('application', 'session_timeout')
        )

        # validating for parent json block
        for key in expected_keys:
            local_config = json_configs
            local_key = key

            # validating for nested child json block
            if type(key) == tuple:
                parent_key, local_key = key
                local_config = json_configs[parent_key]

            if local_key not in local_config.keys():
                raise MissingConfiguration(f'Missing configuration key: {local_key}')
            elif local_config[local_key] is None:
                raise MissingConfiguration(f'Missing configuration value for key: {local_key}')
