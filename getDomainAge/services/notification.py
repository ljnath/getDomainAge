from flask import flash
from getDomainAge.models.enums import NotificationCategory


class NotificationService:
    """
    Service class for showing all kinds of notificatin in the webpage
    """

    def notify_success(self, message: str) -> None:
        """
        method to show success message
        :param message: the message to be flashed
        """
        if message:
            flash(message, NotificationCategory.SUCCESS.value)

    def notify_warning(self, message: str) -> None:
        """
        method to show warning message
        :param message: the message to be flashed
        """
        if message:
            flash(message, NotificationCategory.WARNING.value)

    def notify_error(self, message: str) -> None:
        """
        method to show dannger or error message
        :param message: the message to be flashed
        """
        if message:
            flash(message, NotificationCategory.DANGER.value)
