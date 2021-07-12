import re

from flask import session
from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler
from getDomainAge.models.enums import SessionParam


class LoginService:
    """
    Class responsible for all login and logout service
    """
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler.get_logger(__name__, self.__env.log_path)

    def login(self, email) -> bool:
        """
        method to allow a user to login into the app

        the login process basically checked for a valid email and adds it into the session
        :return successful_login : boolean status of the login process
        """
        successful_login = False

        if email and re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email, re.I):
            session[SessionParam.LOGGED_IN.value] = True
            session[SessionParam.VIEW_ALL.value] = False
            session[SessionParam.EMAIL.value] = email
            successful_login = True
            self.__logger.info(f'Successful login by user with email {email}')
        else:
            self.__logger.warn(f'Failed login by user with invalid email {email}')

        return successful_login

    def logout(self):
        """
        methog to logout a user from the app

        the logout process basically removes the logged-in email from the session and clears it
        """
        temp_email = session[SessionParam.EMAIL.value]
        session.clear()
        self.__logger.info(f'User {temp_email} has logged out')
