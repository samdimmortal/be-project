import os, requests, sys 
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beproject.settings")
django.setup()

# # start parse and let this boy train
# from bs4 import BeautifulSoup
# import newspaper
# import nltk
# from nltk.corpus import stopwords
# from nltk.stem.porter import *
# from datetime import datetime
from app.models import *
# from selenium import webdriver
# from pprint import pprint
# stop = set(stopwords.words('english'))
# stemmer = PorterStemmer()

from selenium import webdriver
from app.parse2 import *

# # sample = ['sasikala', 'modi', 'trump h1b', 'infosys', 'tcs', '']
# sample = []
# if os.environ.get('heroku'):
# 	url = "http://www.news.google.co.in"
# 	r = requests.get(url)
# 	soup = BeautifulSoup(requests.get(url).text, 'lxml')
# 	for link in soup.find_all('a'):
# 		for item in link.text.encode('utf-8', 'replace').split(" "):
# 			item = item.lower()
# 			item = item.replace("'","").replace('"','')
# 			if item not in stop and item != "" and len(item) > 3:
# 				sample.append(item)
# else:
# 	driver = webdriver.Chrome(os.getcwd() + '/chromedriver')

# 	driver.get('http://news.google.com')

# 	sample = []

# 	for i in driver.find_elements_by_css_selector('a'):
# 		for item in i.text.encode('utf-8', 'replace').split(" "):
# 			item = item.lower()
# 			item = item.replace("'","").replace('"','')
# 			if item not in stop and item != "" and len(item) > 3:
# 				sample.append(item)

# 	driver.close()
# sample = list(set(sample))

# print(len(sample))

# pprint(sample)

sample = [
  'air india problems',
  'network programming',
  'donald trump',
  'golang',
  'golang python',
  'hydrogen metal',
  'hyperloop india',
  'iphone x',
  'lenovo problems',
  'mahatma gandhi murder',
  'make in india',
  'mallya',
  'modi india',
  'air deccan',
  'samsung battery explosion',
  'sasikala',
  'palaniswami',
  'pakistan sufi',
  'uttar pradesh elections',
  'income tax department',
  'spacex nasa',
  'falcon wings',
  'trump boeing visit',
  'demonetisation',
  'airline screen seats',
  'russia trump',
  'kim jong nam assassination',
  'jolly llb 2 collections',
  'india australia',
  'Hafiz Saeed pakistan',
  # '',
]

if len(sys.argv) == 3:
  sample = [sys.argv[2]]
  result_count = int(sys.argv[1])

for i in reversed(sample):
  result_count = 100
  if len(sys.argv) == 2:
    result_count = int(sys.argv[1])
  print "Getting {0} results for {1}".format(result_count, i)
  # get_results(i, result_count, force = True, news = False, analysis = False)
  getGoogleResults(i, result_count, news = False, force = False)