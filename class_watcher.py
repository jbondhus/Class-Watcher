#!/usr/bin/python

__title__ = "Class Monitoring Bot"
__author__ = "Jonathan Bondhus"
__version__ = "2.1 beta"

# # Version Information
# 0.1 alpha - Initial prototype
# 0.2 alpha - Simplified some programming, and downgraded from BeautifulSoup 4 to BeautifulSoup 3 because of bugs
# 1.0 beta - Complete overhaul of program structure, re-wrote almost from the ground up
# 1.1 beta - Minor syntax clean-ups and more commenting added. Moved imports into a try-except block so that any errors
#            have a much higher chance of being reported (the modules my email module uses are standard python modules,
#            so withstanding a server error or corrupted python installation they should always be installed)
# 1.2 beta - Added stack trace to email reports and modified email reporting method parameters
# 1.3 beta - Fixed bugs with searching for the course name, improved reliability of matches
# 1.4 beta - Modified for python 3, moved settings to separate file
# 2.0 beta - Added persistence to error reporting - this prevents spamming of identical errors
# 2.1 beta - Fixed working directory bug, fixed Beautiful Soup 4 warning

import os

# Set the working directory to the folder this script is in
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

def report(exception, user_message="Something has gone wrong, debugging information follows:\n\n"):
    """
    Reports any errors that arise

    Defaults:
        user_message = "Something has gone wrong, debugging information follows:\n\n"

    Parameters:
        exception (Exception) - The exception object to report
        user_message (str) - An optional message to include (If included, this will override the default message)
    """

    try:
        root['error_reporter']
    except:
        root['error_reporter'] = ErrorReporting(emailer)

    try:
        root['error_reporter'].report_error(exception, user_message)
        transaction.commit()
    except Exception as e:
        transaction.abort()
        raise Exception("Failed to report the error!") from e


def configure_logging():
    # Sets the logging level
    if settings.logging.log_level.lower() == "disabled":
        log_level = logging.NOTSET
    elif settings.logging.log_level.lower() == "debug":
        log_level = logging.DEBUG
    elif settings.logging.log_level.lower() == "info":
        log_level = logging.INFO
    elif settings.logging.log_level.lower() == "warning":
        log_level = logging.WARNING
    elif settings.logging.log_level.lower() == "error":
        log_level = logging.ERROR
    elif settings.logging.log_level.lower() == "critical":
        log_level = logging.CRITICAL
    else:
        print("Please specify a valid logging option - valid options are as follows:")
        print("Disabled - disables logging")
        print("Debug    - Debug messages and all below")
        print("Info     - Informational messages and all below")
        print("Warning  - Warning messages and all below")
        print("Error    - Error messages and all below")
        print("Critical - Critical messages and all below")
        exit(1)

    if settings.logging.clear_log_on_start:
        with open(settings.logging.log_file_location, 'w'):
            pass

    logging.basicConfig(
        filename=settings.logging.log_file_location,
        level=log_level,
        format=settings.logging.log_format_string,
        datefmt=settings.logging.log_date_format
    )


def initialize():
    """
    Initializes the global variables
    """

    # Make sure the section info object is initialized
    try:
        root['section_info']
    except:
        root['section_info'] = Section(settings.search_url)
        root['section_info'].update()
        transaction.commit()

    # Make sure the URL hasn't changed
    if not root['section_info'].url_equals(settings.search_url):
        root['section_info'] = Section(settings.search_url)
        root['section_info'].update()
        transaction.commit()

        logging.info("The course being watched has changed!")

        # If it has, update the database, notify the user, and quit
        emailer.send(settings.email.to_address, "The course being watched has been changed!",
                     "The course being watched has been "
                     + "changed to " + root['section_info'].get_course_name())
        exit(0)


def main():
    initialize()  # Initialize the persistent variables and the emailer

    # Save whether the section is open before we update
    pre_update_is_section_open = root['section_info'].is_section_open()

    logging.info("Updating section info")
    root['section_info'].update()  # Update the section information

    # After the section has been updated, save the new information about whether or not it is open
    post_update_is_section_open = root['section_info'].is_section_open()

    # If the section has changed, notify the user, otherwise, print a message and exit
    if (pre_update_is_section_open != post_update_is_section_open):
        logging.info("Section status has changed")
        notify(post_update_is_section_open, root['section_info'].get_course_name())
    else:
        logging.info("Nothing has changed, not emailing")

    logging.debug("Committing transaction")

    # Commit the transaction
    transaction.commit()


def notify(is_section_open, course_name):
    """
    Notifies the user whether the section status has changed

    Parameters:
        is_section_open (bool) - Whether or not the section to notify the user about is open
        course_name (str) - The name of the course no notify the user about
    """

    if is_section_open:
        logging.info("Sending email: The course " + course_name + " has opened for registration!")
        subject = "The course " + course_name + " has opened for registration!"  # The subject of the email message
        message = "Go to the following link to view it and verify: \n\n" + settings.search_url
    else:
        logging.info("Sending email: The course " + course_name + " has closed for registration!")
        subject = "The course " + course_name + " has closed for registration!"  # The subject of the email message
        message = "Go to the following link to view it and verify: \n\n" + settings.search_url
    emailer.send(settings.email.to_address, subject, message)
    logging.info("Message sent successfully!")


try:
    # All imports and the call to the main method go in a try/except statement so that we can catch any errors

    try:
        # Try importing the required modules, attempt to email the error if something goes wrong

        # Import settings values
        from Settings import Settings

        settings = Settings()

        import logging

        configure_logging()  # Configure logging first

        # Import the traceback module for retrieving tracback information from exceptions
        import traceback

        # Import modules for the persistent object database
        from ZODB import FileStorage, DB
        import transaction

        # Initialize the persistent database
        storage = FileStorage.FileStorage(settings.database_path)
        db = DB(storage)
        connection = db.open()
        root = connection.root()

        # Import my email module - this must be done first along with traceback (which is needed by email so it must be
        # before email) so if any errors happen importing the rest of the modules they are reported
        from Email import Email

        # Initialize the email object first so that we can send an error message if something breaks
        emailer = Email(
            settings.email.from_name,
            settings.email.from_address,
            settings.email.hostname,
            settings.email.username,
            settings.email.password,
            settings.email.priority,
            settings.email.tls_enabled,
            settings.email.force_tls
        )

        from ErrorReporting import ErrorReporting

        global reporter
        reporter = ErrorReporting(emailer)

        # Import my section information module
        from Section import Section
    except Exception as e:
        report(e)

    main()
except Exception as e:
    try:
        report(e)
    except:
        pass

    logging.critical("Exception! Traceback Follows: \n" + traceback.format_exc())
    raise e

exit(0)  # Exit the program

