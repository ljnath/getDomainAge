class BaseException(Exception):
    """
    Base Exception class in this project
    """
    def __init__(self, message=None):
        super().__init__()
        if message:
            print(message)


class InvalidInput(BaseException):
    """
    Exception class to be raised when any input is invalid
    """
    def __init__(self, message):
        super().__init__()
        print(message)


class UninitializedEnvironment(BaseException):
    """
    Exception class raised when any configuration key or value is missing
    """
    def __init__(self):
        super().__init__()
        print('Environment is uninitilaized, please initilize it before using any of its member')


class MissingConfiguration(BaseException):
    """
    Exception class raised when any configuration key or value is missing
    """
    def __init__(self, message):
        super().__init__()
        print(message)
