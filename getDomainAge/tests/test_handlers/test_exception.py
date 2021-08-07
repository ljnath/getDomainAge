import builtins
from unittest.mock import Mock

from getDomainAge.handlers.exception import BaseException


def test_that_base_exception_prints_message():
    # mocking the builting print method
    builtins.print = Mock()

    try:
        raise BaseException(message='dummy message')
    except BaseException:
        # validating thet print is called and called with the exception message
        builtins.print.assert_called()
        builtins.print.assert_called_with('dummy message')
