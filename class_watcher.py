#!/usr/bin/python

__title__ = "Class Monitoring Bot" # Emails the specified email when a class has a free spot
__author__ = "Jonathan Bondhus"
__version__ = "1.3 beta"

## Version Information
# 0.1 alpha - Initial prototype
# 0.2 alpha - Simplified some programming, and downgraded from BeautifulSoup 4 to BeautifulSoup 3 because of bugs
# 1.0 beta - Complete overhaul of program structure, re-wrote almost from the ground up
# 1.1 beta - Minor syntax clean-ups and more commenting added. Moved imports into a try-except block so that any errors
#            have a much higher chance of being reported (the modules my email module uses are standard python modules,
#            so withstanding a server error or corrupted python installation they should always be installed)
# 1.2 beta - Added tracebacks to email reports and modified email reporting method parameters
# 1.3 beta - Fixed bugs with searching for the course name, improved reliability of matches

## TODO
# - Add persistant storage for last error so that multiple error messages aren't sent repeatedly upon error

## Important Information - Please Read
# This program must be as fail-safe as possible, so import the modules in a try-except (with the email module going
# first) so that unless there is an error with the email module errors can be reported via email. Another important
# thing is thathe __title__ variable must be set in order for this program to function (it's at the beginning of the
# program)

######################### START CONFIGURATION ###########################

# The URL to scrape the information from
search_url = "https://banner.stthomas.edu/pls/banner/prod/bwckschd.p_disp_listcrse?term_in=201420&subj_in=CISC&crse_in=210&crn_in=20807"

# The path to the persistant storage database (this may be absolute or relative, but the program should (haven't tested this) throw an exception if it's read-only)
database_path = "persistent.db"

# Email Settings

# The server settings
hostname = "smtp.gmail.com:587" # The SMTP server hostname
tls_enabled = True    # Whether or not TLS is enabled

# The email username and password
username = "jonathan.bondhus@gmail.com"
password = "qiVBwGoHpLv4MV8MlB46i7PW76B7qPuS1VEEgmM9zF1JLVDjNMMngbgyJTODl4JBChtr42YOw7tBHQ9XjJZn0juqPVJdKsX7GvEa"

from_name = __title__ # The name to appear in the from section
from_address = "jonathan.bondhus@gmail.com" # The address the email message is being sent from
to_address = "jonathan.bondhus@gmail.com" # The address the email message is being sent to

priority = 1 # The priority of the message (1 is the highest, 3 is normal, 5 is the lowest)

########################## END CONFIGURATION ############################

def report_error(exception, user_message="Something has gone wrong, debugging information follows:\n\n"):
    """
    Reports any errors that arise

    Defaults:
        user_message = "Something has gone wrong, debugging information follows:\n\n"

    Parameters:
        exception (Exception) - The exception object to report
        user_message (str) - An optional message to include (If included, this will override the default message)
    """

    message = str(user_message) + traceback.format_exc()
    
    # Make sure that the emailer is initialized, this method MUST not fail
    try:
        emailer
    except:
        emailer = Email(from_name, from_address, hostname, username, password, priority)

    write_message("An error has occured, an attempt will be made to email the information to the address you specified")

    try: # Try to send the email
        emailer.send(to_address, __title__ + " Error", message)
    except Exception as e: # If sending the email fails, write an error message to the screen - logging will be implemented later
        write_message("Sending the error email failed!")
        raise e

def initialize():
    """
    Initializes the global variables
    """

    # Declare global the variables that must be global
    global emailer
    global root

    # Initialize the email object first so that we can send an error message if something breaks
    emailer = Email(from_name, from_address, hostname, username, password, priority)

    # Initialize the persistant database
    storage = FileStorage.FileStorage(database_path)
    db = DB(storage)
    connection = db.open()
    root = connection.root()

    # Make sure the section info object is initialized
    try:
        root['section_info']
    except:
        root['section_info'] = Section(search_url)
        root['section_info'].update()
        transaction.commit()

    # Make sure the URL hasn't changed
    if not root['section_info'].url_equals(search_url):
        root['section_info'] = Section(search_url)
        root['section_info'].update()
        transaction.commit()
        # If it has, update the database, notify the user, and quit
        emailer.send(to_address, "The course being watched has been changed!", "The course being watched has been "
            + "changed to " + root['section_info'].get_course_name())
        sys.exit()

def main():
    # Most exceptions will be handled and reported by the main method
    try:
        initialize() # Initialize the persistent variables and the emailer

        # Save whether the section is open before we update
        pre_update_is_section_open = root['section_info'].is_section_open()

        root['section_info'].update() # Update the section information

        # After the section has been updated, save the new information about whether or not it is open
        post_update_is_section_open = root['section_info'].is_section_open()

        # If the section has changed, notify the user, otherwise, print a message and exit
        if (pre_update_is_section_open != post_update_is_section_open):
            notify(post_update_is_section_open, root['section_info'].get_course_name())
        else:
            write_message("Nothing has changed, not emailing")
            sys.exit()

        # Commit the transaction
        transaction.commit()

    except Exception as e: # If an error occurs anywhere, report it
        report_error(e)
        raise e

def notify(is_section_open, course_name):
    """
    Notifies the user whether the section status has changed

    Parameters:
        is_section_open (bool) - Whether or not the section to notify the user about is open
        course_name (str) - The name of the course no notify the user about
    """

    if is_section_open:
        subject = "The course " + course_name + " has opened for registration!" # The subject of the email message
        message = "Go to the following link to view it and verify: \n\n" + search_url
    else:
        subject = "The course " + course_name + " has closed for registration!" # The subject of the email message
        message = "Go to the following link to view it and verify: \n\n" + search_url   
    emailer.send(to_address, subject, message)

def write_message(message):
    """
    Right now this prints a message to stdout, but I plan to have it log in the future

    Arguments:
        message (str) - The message to display

    Returns: Nothing
    """

    print(str(message))

# Try importing the required modules, attempt to email the error if something goes wrong
try:
    # Import the traceback module for retrieving tracback information from exceptions
    import traceback

    # Import my email module - this must be done first along with traceback (which is needed by email so it must be
    # before email) so if any errors happen importing the rest of the modules they are reported
    from Email import Email

    # Some BS to shut up the interpreter
    import logging
    logging.basicConfig()
    
    # Import system modules (mainly used for exiting the program)
    import os
    import sys
    
    # Import modules for the persistant object database
    from ZODB import FileStorage, DB
    import transaction
    
    # Import my section information module
    from Section import Section
except Exception as e:
    try:
        report_error(e)
    except NameError as e:
        write_message("The email module must not have been able to been imported!")
    raise e

main()
sys.exit() # Exit the program

