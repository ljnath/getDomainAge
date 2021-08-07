from getDomainAge.handlers.log import LogHandler


def test_duplicate_logger():
    logger_1 = LogHandler().get_logger('test-logger', 'test.log')
    logger_2 = LogHandler().get_logger('test-logger', 'test.log')
    assert logger_1 == logger_2


def test_unique_logger():
    logger_1 = LogHandler().get_logger('test-logger-1', 'test.log')
    logger_2 = LogHandler().get_logger('test-logger-2', 'test.log')
    assert logger_1 != logger_2
