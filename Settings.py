
class Settings:
    # The URL to scrape the information from
    search_url = "https://banner.stthomas.edu/pls/banner/prod/bwckschd.p_disp_listcrse?term_in=201420&subj_in=CISC&crse_in=210&crn_in=20807"

    # The path to the persistant storage database (this may be absolute or relative, but the program should (haven't tested this) throw an exception if it's read-only)
    database_path = "persistent.db"

    class Email:
        # Email Settings

        # The server settings
        hostname = "smtp.gmail.com:587" # The SMTP server hostname
        tls_enabled = True    # Whether or not TLS is enabled

        # The email username and password
        username = "jonathan.bondhus@gmail.com"
        password = "qiVBwGoHpLv4MV8MlB46i7PW76B7qPuS1VEEgmM9zF1JLVDjNMMngbgyJTODl4JBChtr42YOw7tBHQ9XjJZn0juqPVJdKsX7GvEa"

        from_name = "Class Monitoring Bot" # The name to appear in the from section
        from_address = "jonathan.bondhus@gmail.com" # The address the email message is being sent from
        to_address = "jonathan.bondhus@gmail.com" # The address the email message is being sent to

        priority = 1 # The priority of the message (1 is the highest, 3 is normal, 5 is the lowest)

    email = Email()