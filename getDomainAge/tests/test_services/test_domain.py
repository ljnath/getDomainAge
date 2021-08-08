from datetime import datetime, timedelta
from unittest.mock import Mock, PropertyMock, patch

import getDomainAge
from getDomainAge.handlers.cache.domain import DomainCacheHandler
from getDomainAge.handlers.environment import Environment
from getDomainAge.services.domain import DomainService
from getDomainAge.tests import with_valid_environment
from getDomainAge.tests.mocked_util import MockedUtil


@with_valid_environment
@patch('getDomainAge.services.domain.DomainService.get_age_of_domain', MockedUtil().get_mocked_age)
def test_get_age_from_urls():
    results = DomainService().get_age_from_urls(['https://ljnath.com/index'])

    assert results[0].age == 5
    assert results[0].domain_name == 'www.ljnath.com'
    assert results[0].url == 'https://ljnath.com/index'


@with_valid_environment
@patch('getDomainAge.services.domain.DomainService.get_age_of_domain', MockedUtil().get_mocked_age)
def test_get_age_of_domains():
    domains = ['https://ljnath.com/index', None]
    results = DomainService().get_age_of_domains(domains)

    assert domains[0] in results.keys()
    assert results[domains[0]] == 5
    assert results[domains[1]] == 'NA'


@with_valid_environment
def test_get_age_of_domain():
    domain_service = DomainService()

    thirty_days_back = datetime.today() - timedelta(days=30)
    sixty_days_back = datetime.today() - timedelta(days=60)

    Environment().memcached_domain.update({'ljnath.com': thirty_days_back.strftime('%Y-%m-%d')})
    domain1_age = domain_service.get_age_of_domain('ljnath.com')

    with patch.object(domain_service, '_DomainService__parse_domain_reg_date', new_callable=PropertyMock) as mocked_method:
        mocked_method.return_value = sixty_days_back.strftime('%Y-%m-%d')
        domain2_age = domain_service.get_age_of_domain('test.com')

    assert domain1_age == 30
    assert domain2_age == 60


@with_valid_environment
def test_get_domain_from_url_no_exception():
    domain_service = DomainService()
    try:
        domain_service.get_age_from_urls(['abc', int, 0.123])
    except Exception:
        assert False, 'Exception should not be raised, it should have been handled property'


@with_valid_environment
def test_get_domain_age_in_days_no_exception():
    domain_service = DomainService()
    Environment().memcached_domain.update({'ljnath.com': 'this is an invalid registration date'})

    try:
        domain_service.get_age_of_domain('ljnath.com')
    except Exception:
        assert False, 'Exception should not be raised, it should have been handled property'


@with_valid_environment
def test_update_and_saving_of_cache():
    domain_service = DomainService()
    with patch.object(domain_service, '_DomainService__parse_domain_reg_date', new_callable=PropertyMock) as mocked_method:
        mocked_method.return_value = datetime.today().strftime('%Y-%m-%d')

        with patch.object(DomainCacheHandler, 'save_to_disk') as mocked_domain_cache_hanlder:
            domain_service.get_age_from_urls(['https://somedomain.com/index.html'])
            mocked_domain_cache_hanlder.assert_called()
