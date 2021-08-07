import builtins
import os
import pickle
from os import path
from pathlib import Path
from unittest.mock import Mock, patch

from getDomainAge.handlers.cache.domain import DomainCacheHandler
from getDomainAge.handlers.environment import Environment
from getDomainAge.tests.mocked_util import MockedUtil


def test_positive_lookup():
    env = Environment()
    env.initialize(MockedUtil().get_valid_configs())
    env.memcached_domain = {'domain.com': '2021-04-05'}

    domain_cache_handler = DomainCacheHandler()
    assert isinstance(domain_cache_handler.lookup('domain.com'), str)
    assert domain_cache_handler.lookup('domain.com') == '2021-04-05'
    Environment.clear()


def test_negative_lookup():
    Environment().initialize(MockedUtil().get_valid_configs())
    domain_cache_handler = DomainCacheHandler()
    assert domain_cache_handler.lookup('domain.com') is None
    Environment.clear()


def test_update_of_cache():
    Environment().initialize(MockedUtil().get_valid_configs())
    domain_cache_handler = DomainCacheHandler()
    domain_cache_handler.update('mydomain.com', '2021-08-07')

    assert domain_cache_handler.lookup('mydomain.com') == '2021-08-07'
    Environment.clear()


def test_save_to_disk():
    env = Environment()
    env.initialize(MockedUtil().get_valid_configs())
    env.memcached_domain = {'domain.com': '2021-04-05'}

    domain_cache_handler = DomainCacheHandler()
    domain_cache_handler.save_to_disk()
    assert os.path.isfile(Environment().cached_domain_path)
    Environment.clear()


def test_load_from_disk():
    env = Environment()
    env.initialize(MockedUtil().get_valid_configs())
    cached_content = {'domain.com': '2021-04-05'}

    domain_cache_handler = DomainCacheHandler()
    domain_cache_handler.load_from_disk()
    assert env.memcached_domain == cached_content
