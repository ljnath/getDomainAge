from typing import Dict, List
from urllib.parse import urlparse

import requests
from datetime import datetime
from bs4 import BeautifulSoup
from getDomainAge.handlers.cache.domain import DomainCacheHandler
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.csv_result import CsvResult


class DomainService:
    """
    Service class for domain processing like parsing domain from URL and parsing the result
    """

    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(__name__, self.__env.log_path)
        self.__domain_cache_handler = DomainCacheHandler()

    def __get_domain_from_url(self, url: str) -> str:
        """
        Gets the domain name from a given URL using urlparser
        :param url : string for which the domain name has to be extracted
        :return domain_name : returns the domain name as string
        """
        domain_name = None
        try:
            result = urlparse(url)
            domain_name = result.netloc if result.netloc else result.path
        except ValueError as parse_error:
            self.__logger.warning(f'Failed to parse domain name from URL {url}')
            self.__logger.exception(parse_error, exec_info=True)
        else:
            domain_name = f"{'www.' if not domain_name.startswith('www.') else ''}{domain_name}"
        finally:
            return domain_name

    def __get_domain_age_in_days(self, reg_date: str) -> int:
        """
        Method to get the age of domain from its registration date in days
        :param reg_date : registered_date as string is the registration date of the domain
        :return age : age as integer is the age in days
        """
        domain_age = 0
        try:
            registered_date_format = '%Y-%m-%d'
            date_of_registration = datetime.strptime(reg_date, registered_date_format)
            delta = datetime.today() - date_of_registration
            domain_age = delta.days
        except ValueError as value_error:
            self.__logger.error(f'Failed to calculate the domain age from domain registration date {reg_date}')
            self.__logger.exception(value_error, exc_info=True)

        return domain_age

    def __parse_domain_reg_date(self, domain_name: str) -> str:
        """
        Method to get the registered date for a given URL
        :param domain_name : domain_name as string for which the registered name needs to be parsed
        :return reg_date: returns list of sets with domain and its registration date
        """
        registration_date = ''
        try:
            response = requests.get(f'{self.__env.whois_url}/{domain_name}')
            if response.status_code != 200:
                self.__logger.error(
                    f'Received invalid response from remote URL {self.__env.whois_url}. '
                    f'Expected 200, received {response.status_code}')
            else:
                # parsing logic is volatile as it will break if whois.com changes their site layout
                beautiful_soup = BeautifulSoup(response.text, 'html.parser')
                div_blocks = beautiful_soup.find_all('div', attrs={'class': 'df-block'})
                if div_blocks and div_blocks[0].find_all('div')[10].text.lower().startswith('registered on'):
                    registration_date = div_blocks[0].find_all('div')[11].text
                self.__logger.info(
                    f'Parsed domain info from whois.com. Domain {domain_name} was registered on {registration_date}')
        except Exception as e:
            self.__logger.error(f'Failed to parse domain ({domain_name}) information from remote')
            self.__logger.exception(e, exc_info=True)

        return registration_date

    def get_age_of_domain(self, domain_name: str) -> int:
        """
        Method to get the domain age from a passed domain name.
        It checks if the domain name is already cached, if yes it returns from the cache
        else it parses the registration date from whois.com and calculates the doamin age in days
        :param domain_name : domain name whose age needs to be retrived
        """
        reg_date = self.__domain_cache_handler.lookup(domain_name)

        if reg_date:
            self.__logger.info(
                f'Domain registration details found in local cache. Domain {domain_name} was registered on {reg_date}')
        else:
            self.__logger.debug(f'Failed to get domain ({domain_name}) information from cache, trying to parse from remote')
            reg_date = self.__parse_domain_reg_date(domain_name)
            self.__domain_cache_handler.update(domain_name, reg_date)

        return self.__get_domain_age_in_days(reg_date)

    def get_age_of_domains(self, domains: List[str]) -> Dict[str, int]:
        """
        Method to get the age of each domains from the list of domains.
        Internally it does a lookup in the cache and returns the result from it.
        If it is not prsent in the cache, it parses the information from remote site ans returns the same
        :param domains : list of domains which needs to be processed
        :return result : a dictionary containing all the domains along with its age
        """
        result = {}
        cache_count = len(self.__env.memcached_domain.keys())
        for domain in domains:
            age = 'NA'
            if not domain:
                self.__logger.warning(f'Invalid domain name {domain}')
            else:
                age = self.get_age_of_domain(domain)

            result.update({domain: age})

        # saving cache to disk if domain count in the cache has changed
        if cache_count != len(self.__env.memcached_domain.keys()):
            self.__domain_cache_handler.save_to_disk()

        return result

    def get_age_from_urls(self, urls: list) -> List[CsvResult]:
        """
        Method to parse the domain name from URLs and calcualte its age (in days).
        :param urls : URLs as a list of strings which needs to be processed
        :return csv_results : list of 'CsvResult'
        """
        csv_results = []
        cache_count = len(self.__env.memcached_domain.keys())
        for url in urls:
            domain_name = self.__get_domain_from_url(url)
            age = self.get_age_of_domain(domain_name)
            csv_results.append(CsvResult(url, domain_name, age))

        # saving cache to disk if domain count in the cache has changed
        if cache_count != len(self.__env.memcached_domain.keys()):
            self.__domain_cache_handler.save_to_disk()

        return csv_results
