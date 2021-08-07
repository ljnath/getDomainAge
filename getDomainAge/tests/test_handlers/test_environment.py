import pytest
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.exception import UninitializedEnvironment


def test_uninitialized_environment():
    with pytest.raises(UninitializedEnvironment):
        Environment().app_name


def test_singleton_environment():
    env_1 = Environment()
    env_2 = Environment()
    assert env_1 == env_2
