"""
Class responsible for acting as metaclass for generation of singleton classes
"""


class Singleton(type):
    """
    Class responsible for acting as metaclass for generation of singleton classes
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Method to create an intance of the class if it is not created before,
        else return the already created one
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args,
                **kwargs
            )
        return cls._instances[cls]

    def clear(cls):
        """
        Method to delete the singleton instance of the class
        """
        try:
            del Singleton._instances[cls]
        except KeyError:
            pass
