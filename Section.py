# Import requests for performing GET requests
import requests

# Import BeautifulSoup for parsing the html
from BeautifulSoup import BeautifulSoup

# Import the regular expression module for parsing text
import re

# This class has to be persistant to store the data
from persistent import Persistent

# Defines course section objects
class Section(Persistent):
	def __init__(self, search_url):
		"""
		Generates a new section object with the url to pull the information from as a parameter

		Parameters:
			search_url (str) - The URL to pull the section (course) information from
		"""

		# Make sure the variables are the correct type
		if not isinstance(search_url, str):
			raise TypeError("The search url must be a string")

		try:
			requests.get(search_url, timeout=60)
		except Exception, e:
			raise ValueError("Please check that it is possible to connect to the URL you specified!")

		self.search_url = str(search_url)
		self.html = None
		self.soup = None

	def update(self):
		"""
		Updates the HTML
		"""

		response = requests.get(self.search_url, timeout=5) # Query the search url
		self.html = response.text # Get the html from the response
		self.soup = BeautifulSoup(self.html) # Parse the HTML to create a BeautifulSoup object (similar to a parse tree)

	def is_section_open(self):
		"""
		Gets whether the section is open from the html
		"""

		# Make sure the HTML instance variable isn't null
		if (self.soup == None):
			self.update()

		# If the section status isn't found, throw an error, otherwise return the status
		if (self.soup).body.find("b", text="Section Closed") != None:
			return False
		elif (self.soup).body.find("b", text="Open") != None:
			return True
		else:
			raise Exception("The status of the section could not be found!")

	def get_course_name(self):
		"""
		Gets the course name from the html
		"""

		# Make sure the soup instance variable isn't null
		if (self.soup == None):
			self.update()

		# The absolute name (taken straight from the HTML)
		absolute_name = str(self.soup.find("th", "ddtitle").a.contents[0])

		# The formatted name (parsed with a regular expression from the HTML)
		queried_name = re.search('[A-Z]{4}\s[0-9]{3}', absolute_name).group()

		if (queried_name != None): # If we aren't able to format it, set the class name to the absolute name (the one
								   # before formatting) as a fail-over
			course_name = queried_name
		else:
			course_name = absolute_name

		return course_name		

	def url_equals(self, url):
		"""
		Checks whether the url passed equals the saved url of the section

		Parameters:
			url (str) - The URL to compare
		"""

		# Make sure the variables are the correct type
		if not isinstance(url, str):
			raise TypeError("The url must be a string")

		return self.search_url == str(url)

