from unittest.mock import patch
import os
import pytest
from getDomainAge.handlers.config import ConfigHandler
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.exception import (InvalidInput,
                                             UninitializedEnvironment, MissingConfiguration)
from getDomainAge.handlers.log import LogHandler
from getDomainAge.tests.mocked_util import MockedUtil


def test_logger():
    logger_1 = LogHandler().get_logger('test-logger', 'test.log')
    logger_2 = LogHandler().get_logger('test-logger', 'test.log')
    assert logger_1 == logger_2


def test_uninitialized_environment():
    with pytest.raises(UninitializedEnvironment):
        Environment().app_name


def test_singleton_environment():
    env_1 = Environment()
    env_2 = Environment()
    assert env_1 == env_2


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
        config_handler = ConfigHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/invalid1.json'))
        config_handler.load()


def test_config_handler_with_invalid_json2():
    with pytest.raises(MissingConfiguration):
        config_handler = ConfigHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/invalid2.json'))
        config_handler.load()

def test_config_handler_with_valid_json():
    try:
        config_handler = ConfigHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/valid.json'))
        config_handler.load()
    except MissingConfiguration:
        assert False, 'Exception should not be raised when valid JSON file is used'
