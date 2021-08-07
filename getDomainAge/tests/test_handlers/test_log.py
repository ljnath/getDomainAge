from getDomainAge.handlers.log import LogHandler


def test_logger():
    logger_1 = LogHandler().get_logger('test-logger', 'test.log')
    logger_2 = LogHandler().get_logger('test-logger', 'test.log')
    assert logger_1 == logger_2
