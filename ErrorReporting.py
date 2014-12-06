from Settings import Settings

settings = Settings()

import traceback

import logging

# This class has to be persistent
from persistent import Persistent


class ErrorReporting(Persistent):
    def __init__(self, emailer):
        """
        Generates a new error reporting object

        Parameters:
            emailer (Email) - The emailer to use for reporting errors
        """

        self.emailer = emailer
        self.last_message = ""

    def report_error(self, exception, user_message="Something has gone wrong, debugging information follows:\n\n"):
        """
        Reports any errors that arise

        Defaults:
            user_message = "Something has gone wrong, debugging information follows:\n\n"

        Parameters:
            exception (Exception) - The exception object to report
            user_message (str) - An optional message to include (If included, this will override the default message)
        """

        message = str(user_message) + traceback.format_exc()

        if self.last_message == message or not settings.only_send_different:
            logging.info("Last message identical to current message, not re-sending")
        else:
            self.last_message = message

            try:  # Try to send the email
                self.emailer.send(settings.email.to_address, "Class Monitoring Bot" + " Error", message)
            except Exception as e:
                logging.critical("Sending the error email failed!")
                raise Exception("Sending the error email failed!") from e