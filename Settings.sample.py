
class Settings:
    # The URL to scrape the information from
    search_url = ""

    # The path to the persistant storage database (this may be absolute or relative, but the program should (haven't tested this) throw an exception if it's read-only)
    database_path = "persistent.db"

    class Email:
        # Email Settings

        # The server settings
        hostname = "" # The SMTP server hostname - in the format hostname:port
        tls_enabled = True    # Whether or not TLS is enabled

        # The email username and password
        username = ""
        password = ""

        from_name = "Class Monitoring Bot" # The name to appear in the from section
        from_address = "" # The address the email message is being sent from
        to_address = "" # The address the email message is being sent to

        priority = 1 # The priority of the message (1 is the highest, 3 is normal, 5 is the lowest)