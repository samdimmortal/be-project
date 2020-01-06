import pdb, os
import selenium, requests
from app.models import *
from app.parse2 import *
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import *


stop = list(set(stopwords.words('english')))
stemmer = PorterStemmer()
# stemmer2 = SnowballStemmer()
def analyseSource(query = "", url = ""):

	if query == "":
		query = webSearch.objects.all().first().queryText

	search = webSearch.objects.get(queryText = query)
	if query == "":
		query = search.results.all()[0].url
	
	all_results = []
	for r in search.results.all():
		all_results.append([r.url, r.text, r.keywords.split(), r.title])
	
	# converting object to dic data structures
	for i in all_results:
		i = {
			'url' : i[0],
			'text' : i[1],
			'keywords' : i[2],
			'title' : i[3],
			'sentences' : [],
			'words' : [],
		}


	# source = url

	data = {
		'search' : query,
		'url' : url,
		'similar' : [],
		'related' : [],
		'duplicates' : [],
		'sub' : [],
		'super' : [],
	}

	for i in all_results:
		i['sentences'] = [j for j in nltk.sent_tokenize(i.get('text'))]
		i['words'] = [stemmer.stem(j.lower()) for j in nltk.word_tokenize(i['sentences']) if j.strip().lower() not in stop]


	source = {}

	for i in all_results:
		if i.url == url:
			source = i
			all_results.remove(i)
			break

	# ready tokenized source, all_results


	return data

