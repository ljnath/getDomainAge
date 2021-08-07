class CsvResult:
    def __init__(self, url: str, domain_name: str = '', age: int = 0):
        self.__url = url
        self.__domain_name = domain_name
        self.__age = age

    @property
    def url(self):
        return self.__url

    @property
    def domain_name(self):
        return self.__domain_name

    @property
    def age(self):
        return self.__age
