from typing import List

import pytest
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.exception import UninitializedEnvironment
from getDomainAge.tests.mocked_util import MockedUtil


def test_uninitialized_environment():
    Environment.clear()
    with pytest.raises(UninitializedEnvironment):
        Environment().app_name


def test_singleton_environment():
    env_1 = Environment()
    env_2 = Environment()
    assert env_1 == env_2


def test_properties():
    env = Environment()
    env.initialize(MockedUtil().get_valid_configs())
    from getDomainAge.models.database.tables import Jobs

    workspace_path = 'my_workspace'
    assert env.app_name == 'getDomainAge'
    assert env.app_version == 0.3
    assert env.workspace_path == workspace_path
    assert env.db_path == f'{workspace_path}/domain.db'
    assert env.cached_domain_path == f'{workspace_path}/domain.cache'
    assert env.log_path == f'{workspace_path}/logs/app.log'
    assert env.result_directory == f'{workspace_path}/results'
    assert env.server_host == 'valid_host'
    assert env.server_port == 80
    assert not env.server_debug_mode
    assert env.smtp_host == 'smtp-host'
    assert env.smtp_port == 25
    assert env.smtp_username == 'smtp-username'
    assert env.smtp_password == 'smtp-password'
    assert env.smtp_sender_email == 'smtp-sender-email'
    assert env.app_job_per_page == 10
    assert env.app_session_timeout == 10

    env.memcached_domain = {'domain.com': '2021-08-08'}
    assert env.memcached_domain['domain.com'] == '2021-08-08'

    dummy_job = Jobs('ljnath@ljnath.com', 1628358880, 'PENDING', 'ljnath.com')
    env.memcached_jobs = [dummy_job]
    assert isinstance(env.memcached_jobs, List)
    assert env.memcached_jobs[0] == dummy_job

    assert env.whois_url == 'https://www.whois.com/whois/'
    assert env.api_secrect_key == 'this-is-my-secret-key'

    Environment.clear()
