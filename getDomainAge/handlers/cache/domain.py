import os
import pickle
from datetime import date

from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler


class DomainCacheHandler:
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(__name__, self.__env.log_path)

    def lookup(self, domain_name: str) -> date:
        """
        Checkes if result of a domain name is already present in local cache
        :pram domain_name : domain_name in string which needs to be checked in the local cache
        :return : returns the domain registrated date for a given domain
        """
        if domain_name in self.__env.memcached_domain.keys():
            self.__logger.debug(f'Found domain info on {domain_name} in the cache')
            return self.__env.memcached_domain[domain_name]

        # returning None if the info is not preset in the cache
        return None

    def update(self, domain_name: str, reg_date: str):
        """
        Method to update local cache with domain_name and registration date
        :param domain_name : domain name to cache
        :param reg_date : registration date of the domain name to cache
        """
        self.__env.memcached_domain[domain_name] = reg_date

    def save_to_disk(self):
        """
        Method to save the domain cahce onto disk
        """
        try:
            with open(self.__env.cached_domain_path, 'wb') as file_handler:
                pickle.dump(self.__env.memcached_domain, file_handler)
                self.__logger.info('Successfully saved domain cache to disk')
        except pickle.PickleError as pe:
            self.__logger.error(f'Failed to save cached domain onto {self.__env.cached_domain_path}')
            self.__logger.exception(pe, exc_info=True)

    def load_from_disk(self):
        """
        Method to load cache from disk
        """
        if os.path.exists(self.__env.cached_domain_path):
            self.__logger.debug(f'Domain cache file found at {self.__env.cached_domain_path} ; trying to load it now')
            try:
                with open(self.__env.cached_domain_path, 'rb') as file_handler:
                    self.__env.memcached_domain = pickle.load(file_handler)
                    self.__logger.info(
                        f'Successfully loaded {len(self.__env.memcached_domain.keys())} domain details from cache file '
                        f'{self.__env.cached_domain_path}')
            except pickle.PickleError as pe:
                self.__env.memcached_domain = {}
                self.__logger.error(f'Failed to load cached domain from {self.__env.cached_domain_path}')
                self.__logger.exception(pe, exc_info=True)
