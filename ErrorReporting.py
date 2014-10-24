from Settings import Settings
settings = Settings()

import traceback

from Email import Email

import logging

# This class has to be persistant to store the data
from persistent import Persistent

class ErrorReporting(Persistent):
    def __init__(self, emailer):
        self.emailer = emailer

    def report_error(self, exception, user_message="Something has gone wrong, debugging information follows:\n\n"):
        """
        Reports any errors that arise

        Defaults:
            user_message = "Something has gone wrong, debugging information follows:\n\n"

        Parameters:
            emailer (Email) - The email object to use to send the message
            exception (Exception) - The exception object to report
            user_message (str) - An optional message to include (If included, this will override the default message)
        """

        message = str(user_message) + traceback.format_exc()

        try: # Try to send the email
            self.emailer.send(settings.email.to_address, "Class Monitoring Bot" + " Error", message)
        except Exception as e: # If sending the email fails, write an error message to the screen - logging will be implemented later
            logging.critical("Sending the error email failed!")
            raise Exception("Sending the error email failed!") from e