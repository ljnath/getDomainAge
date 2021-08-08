import os

from getDomainAge.handlers.cache.domain import DomainCacheHandler
from getDomainAge.handlers.environment import Environment
from getDomainAge.tests import with_valid_environment


@with_valid_environment
def test_positive_lookup():
    env = Environment()
    env.memcached_domain = {'domain.com': '2021-04-05'}

    domain_cache_handler = DomainCacheHandler()
    assert isinstance(domain_cache_handler.lookup('domain.com'), str)
    assert domain_cache_handler.lookup('domain.com') == '2021-04-05'


@with_valid_environment
def test_negative_lookup():
    domain_cache_handler = DomainCacheHandler()
    assert domain_cache_handler.lookup('somedomain.com') is None


@with_valid_environment
def test_update_of_cache():
    domain_cache_handler = DomainCacheHandler()
    domain_cache_handler.update('mydomain.com', '2021-08-07')

    assert domain_cache_handler.lookup('mydomain.com') == '2021-08-07'


@with_valid_environment
def test_save_to_disk():
    env = Environment()
    env.memcached_domain = {'domain.com': '2021-04-05'}

    domain_cache_handler = DomainCacheHandler()
    domain_cache_handler.save_to_disk()
    assert os.path.isfile(Environment().cached_domain_path)


@with_valid_environment
def test_load_from_disk():
    env = Environment()
    cached_content = {'domain.com': '2021-04-05'}

    domain_cache_handler = DomainCacheHandler()
    domain_cache_handler.load_from_disk()
    assert env.memcached_domain == cached_content
