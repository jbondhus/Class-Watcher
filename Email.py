# Import smtplib for the actual sending functionality
import smtplib

# Import the email modules we'll need
from email.message import Message

# Version Information (follows semantic versioning)
# 1.0 - The initial release candidate (versions before this were undocumented)
# 1.1 - Reformatted exception handling

# This class defines email objects. They are constructed with the server and sender information, and sent with the send method
class Email:
    def __init__(self, from_name, from_address, hostname, username, password, priority=3, tls_enabled=True,
                 force_tls=True):
        """
        Constructs an email object

        Parameters:
            from_name (str) - The name that will be displayed in the from information (e.g. "John Doe")
            from_address (str) - The email address to send the email from (e.g. "you@domain.com")
            hostname  (str) - The hostname of the SMTP server to send the message through (e.g. "smtp.gmail.com:587" for Gmail)
            username  (str) - The username to authenticate to the SMTP server with (e.g. "you@domain.com")
            password  (str) - The password to authenticate to the SMTP server with
            [priority] (int) - The priority of the message, from 1 to 5, where 1 is the highest, 3 is normal, and 5 is the lowest - default is 3
            [tls_enabled] (bool) - Whether to enable or disable TLS encryption - default is enabled
        """

        # Make sure the variables are the correct type
        if not isinstance(hostname, str):
            raise TypeError("The hostname must be a string")
        if not isinstance(from_address, str):
            raise TypeError("The from address must be a string")
        if not isinstance(priority, int) or priority < 0 or priority > 5:
            raise TypeError("The priority must be an integer between 0 and 5")
        if not isinstance(tls_enabled, bool):
            raise TypeError("Whether tls is enabled must be a boolean value")
        if not isinstance(force_tls, bool):
            raise TypeError("Whether tls is forced must be a boolean value")

        self.hostname = str(hostname)
        self.from_name = str(from_name)
        self.from_address = str(from_address)
        self.username = str(username)
        self.password = str(password)
        self.priority = int(priority)
        self.tls_enabled = bool(tls_enabled)
        self.force_tls = bool(force_tls)

    def send(self, to_address, subject, message):
        """
        Generates and sends the email with the parameters specified

        Parameters:
            to_address (str) - The email address to send the (e.g. "target@domain.com")
            subject (str) - The subject of the email message
            message (str) - The email message data
        """

        # Make sure the variables are the correct type
        if not isinstance(to_address, str):
            raise TypeError("The destination address must be a string")

        subject = str(subject)
        message = str(message)

        # Create a new email message object
        m = Message()

        # Set the message object's attributes
        m['From'] = str(self.from_name)
        m['X-Priority'] = str(self.priority)
        m['Subject'] = str(subject)

        # Set the payload (message) for the message object
        m.set_payload(message)

        # Try to connect to the server
        try:
            server = smtplib.SMTP(self.hostname, timeout=5)
        except Exception as e:
            raise Exception("Failed to connect to the email server!") from e

        # Greet the server
        server.ehlo()

        # Check for and enable TLS if requested
        if self.tls_enabled:
            try:
                server.starttls()
            except:
                if self.force_tls:
                    raise Exception("TLS failed to start and but is set to be required!")
                else:
                    self.warning("TLS failed to start. Proceeding without encryption!")

        try:  # Try to login, if it fails, write an error message and raise an exception
            server.login(self.username, self.password)
        except Exception as e:
            raise Exception("Server login failed, please check username and password!") from e

        # Try to send the email, if it fails, write an error message and raise an exception
        try:
            server.sendmail(str(self.from_address), str(to_address), m.as_string())
        except Exception as e:
            raise Exception("Sending mail failed!") from e

        server.close()