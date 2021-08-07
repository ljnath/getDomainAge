import os
from pathlib import Path
from unittest.mock import patch

import pytest
from getDomainAge.handlers.config import ConfigHandler
from getDomainAge.handlers.exception import InvalidInput, MissingConfiguration
from getDomainAge.tests.mocked_util import MockedUtil

files_directory = f'{Path(__file__).parent.parent.resolve()}/files'


def test_config_handler_with_invalid_input():
    with pytest.raises(InvalidInput):
        ConfigHandler(None)


@patch('os.path.exists', MockedUtil().get_false)
def test_config_handler_with_missing_input():
    with pytest.raises(InvalidInput):
        ConfigHandler('sample.config')


@patch('os.path.exists', MockedUtil().get_true)
@patch('os.path.isfile', MockedUtil().get_false)
def test_config_handler_with_directory():
    with pytest.raises(InvalidInput):
        ConfigHandler('directory')


@patch('os.path.exists', MockedUtil().get_true)
@patch('os.path.isfile', MockedUtil().get_true)
def test_config_handler_with_valid_input():
    try:
        ConfigHandler('sample.json')
    except InvalidInput:
        assert False, 'No exception should be raised, if config file is correct'


def test_config_handler_with_invalid_json1():
    with pytest.raises(MissingConfiguration):
        json_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{files_directory}/invalid1.json')
        config_handler = ConfigHandler(json_filepath)
        config_handler.load()


def test_config_handler_with_invalid_json2():
    with pytest.raises(MissingConfiguration):
        json_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{files_directory}/invalid2.json')
        config_handler = ConfigHandler(json_filepath)
        config_handler.load()


def test_config_handler_with_valid_json():
    try:
        json_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{files_directory}/valid.json')
        config_handler = ConfigHandler(json_filepath)
        config_handler.load()
    except MissingConfiguration:
        assert False, 'Exception should not be raised when valid JSON file is used'
