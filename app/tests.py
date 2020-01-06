from django.test import TestCase
from app.models import webSearch, WebResource
from app.parse2 import get_results
# Create your tests here.

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import string, random, time, os

characters = string.ascii_letters

class apptestCases(TestCase):

	def random_string(self):
		return random.choice(['a','b','c','dog','cat'])

	def makeResults(self):
		sample = ['protest india', 'gandhi murder', 'isis mumbai']
		for q in sample:
			print len(get_results(q, 50))

	def testName(self):
		self.makeResults()
		