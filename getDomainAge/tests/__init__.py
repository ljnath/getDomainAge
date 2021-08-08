from getDomainAge.handlers.environment import Environment
from getDomainAge.tests.mocked_util import MockedUtil


def with_valid_environment(calling_function):
    """
    decorator create and destory the environment before and after running a test
    """
    def inner_funtion(*args, **kwargs):
        # creating and intializng environment
        Environment().initialize(MockedUtil().get_valid_configs())

        # invoking calling_function; in this case this will be the test
        # storing the output in variable 'result'
        result = calling_function(*args, **kwargs)

        # destorying the singleton instance of environment
        Environment.clear()

        # returning 'result'
        return result

    return inner_funtion
