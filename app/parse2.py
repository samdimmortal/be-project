from __future__ import division
import matplotlib.pyplot as plt
import math
import os, requests, sys, string
from bs4 import BeautifulSoup
import newspaper
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.porter import *
from datetime import datetime
from app.models import *
from selenium import webdriver
from pprint import pprint

from multiprocessing import Process

from django.core.exceptions import MultipleObjectsReturned

stop = set(stopwords.words('english'))
stopwords_hash = {w:1 for w in stop}
stemmer = PorterStemmer()
punctuation = string.punctuation
from pattern.en import parse, wordnet
from pattern.vector import words, count, PORTER, Document, Model, KMEANS, LEMMA, TFIDF, HIERARCHICAL
from pattern.web import plaintext, find_urls, strip_between

# similar_sentence_threshold = 0.4
# similar_articles = 0.7

def plot_graph(a,b):
	try:
		plt.plot([i for i in a], [0 for i in b], 'ro')
		plt.bar(a, b, width=0.8, color='r')
		plt.show()
	except:
		print "Plotting Failed"
		pass


def parseURL(url, force = False):
	"Parses the given url and saves it to Database"
	try:
		wr = WebResource.objects.get(url = url)
	except MultipleObjectsReturned:
		WebResource.objects.filter(url = url).delete()
	except:
		pass

	wr, created = WebResource.objects.get_or_create(url = url)
	if created or force:
		# print "Parsing and Caching {0}".format(url)
		try:
			a = newspaper.Article(url)
			a.download()
			a.parse()
			text = a.text
			title = a.title

			if 'books.google' in url:
				text = ''

			wr.text = str(text.encode('utf-8', 'replace').lower())
			wr.title = a.title
			wr.urls = ",".join(find_urls(strip_between("<body*>","</body", text)))
			wr.save()
			print "  PARSED ", url
		except:
			print "  Failed"
	return wr

def getGoogleResults(query, quantity, news = False, force = False):
	news = False
	all_results = []
	query = query.replace('_','%20')
	breakdown = 50

	if breakdown > quantity:
		breakdown = quantity

	newsParams = ''
	if news:
		newsParams = '&tbm=nws'

	for i in range(0, int(quantity), breakdown):
		if i == 0:
			url = 'https://www.google.com/search?q={0}&num={1}{2}'.format(query, breakdown, newsParams)
		else:
			url = 'https://www.google.com/search?q={0}&num={1}&start={2}{3}'.format(query, breakdown, i, newsParams)

		if os.environ.get('heroku'):
			soup = BeautifulSoup(requests.get(url).text, 'lxml')
			for link in soup.find_all('a'):
				href = link.get('href')
				if '/url?q=' in href and 'webcache' not in href:
					href = href.replace('/url?q=', '')
					href = href[:href.index('&sa')]
					all_results.append(href)

		else:
			driver = webdriver.Chrome(os.getcwd()+'/chromedriver')
			driver.set_window_size(0,0)
			driver.get(url)
			if news:
				for result in driver.find_elements_by_css_selector('div.g'):
					for css in ['a.l', 'a.top']:
						try:
							url = result.find_element_by_css_selector('a.l').get_attribute('href')
							if url:
								all_results.add(url)
						except: pass
			else:
				for result in driver.find_elements_by_css_selector('.rc'):
					url = result.find_element_by_css_selector('a').get_attribute('href')
					if "youtube.co" not in url:
						if url in all_results:
							print "Duplicate Results"
						else:
							all_results.append(url)
			driver.close()

	print 'Received {0} results'.format(len(all_results))
	queue = [] # Queue to line up Processes and run them later as required

	for i in all_results:
		print "Adding to Queue:", i
		queue.append(Process(target=parseURL, args=(i, force)))

	# Run the queued Processes
	for index, p in enumerate(queue):
			if index>=4:
					while queue[index-4].is_alive():
							pass
					p.start()
			else:
					p.start()
	else:
		while sum([0]+[1 for p in queue if p.is_alive()]) > 0:
			pass

	return all_results # Return the results once finished Parsing


def match_rows(a, b):
	a_ones = np.count_nonzero(a)
	b_ones = np.count_nonzero(b)

	comparison = (a==b)

	cross_product = a*b
	intersection = np.count_nonzero(cross_product)
	union = a_ones+b_ones-intersection

	if a_ones+b_ones>0 and union > 0:
		score = intersection/union
	else:
		score = 0

	return score

def build_model(results = []):
	documents = [Document(i.get('text'), name=i.get('url'), description=i.get('index'), stemmer = LEMMA) for i in results]
	m = Model(documents, weight = TFIDF)

	y,x = 1,len(m.features)
	model = np.zeros((y,x))

	sentence_dict = {}
	model_sentences = []
	for i_index, i in enumerate(documents):
		sentences =  sent_tokenize(results[i_index].get('text').lower())

		dy, dx = len(sentences), x
		for s_index, s in enumerate(sentences):
			s_words = {w:1 for w in words(s, stemmer = LEMMA, stopwords = False) if not stopwords_hash.get(w)}
			if len(s_words) < 5:
				continue
			model_sentences.append(s)
			model = np.append(model, [[1 if s_words.get(w) else 0 for w in m.features]], 0)
			sentence_dict[model.shape[0]-1] = i.name
			# model_sentences[model.shape[0]-1] = s

	model = np.delete(model, (0), 0)

	return model, m, model_sentences, sentence_dict

def get_similar_rows(model = np.array((1,1)), sentences = [], sentence_dict = {}):
	print len(sentences)
	print model.shape

	y,x = model.shape
	similar_rows = []
	for i in range(y):
		source = sentence_dict.get(i)
		for j in range(i,y):
			dest = sentence_dict.get(j)
			if source==dest or i==j: continue
			
			score = match_rows(model[i], model[j])

			if score > 0.7:
				similar_rows.append([i,j])
				# print sentences[i]
				# print sentences[j]

	return similar_rows


def find_similarity(results = []):
	model, m, sentences, sentence_dict = build_model(results)
	similar_rows = get_similar_rows(model, sentences, sentence_dict)

	list_of_sim_docs = []

	if similar_rows:
		print "Number of similar sentences {0} repetitions over {1}".format(len(similar_rows), len(sentences))
		for i in results:
			try:
				source = i.get('url')
				source_len = len([1 for s,s_name in sentence_dict.iteritems() if s_name == source])
				for j in results:
					if i==j: continue

					dest = j.get('url')
					dest_len = len([1 for s,s_name in sentence_dict.iteritems() if s_name == dest])

					matched_sentences = [1 for s in similar_rows if sentence_dict[s[0]]==source and sentence_dict[s[1]]==dest]

					similarity = 0

					if dest_len > 0:
						similarity = len(matched_sentences)/min([dest_len, source_len])
						# similarity = len(matched_sentences)/(source_len+dest_len-len(matched_sentences))

					if similarity > 0.4 and similarity < 0.8:
						print "Similar  document [{1} s]{0} [{3} s]{2} [{4}] sim[{5} match s]".format(source[:10], source_len, dest[:10], dest_len, similarity, len(matched_sentences))
					elif similarity >= 0.8 and similarity < 1.0:
						print "Highly-Plagarised documents [{1} s]{0} [{3} s]{2} [{4}] sim[{5} match s]".format(source[:10], source_len, dest[:10], dest_len, similarity, len(matched_sentences))
					elif similarity ==1:
						print "Exactly-Plagarised documents [{1} s]{0} [{3} s]{2} [{4}] sim[{5} match s]".format(source[:10], source_len, dest[:10], dest_len, similarity, len(matched_sentences))

					if similarity > 0.4 and similarity < 1:
						list_of_sim_docs.append({
							'source' : source,
							'dest' : dest,
							'score' : similarity
							})
					if similarity > 1:
						print 'Error'
			except: pass	
	else:
		pass

	return list_of_sim_docs, model, m
	


def get_results(query, quantity, force = False, news = False, analysis = True):
	query = query.lower()
	start = datetime.now()

	query = query.replace('_','%20')
	breakdown = 50

	if breakdown > quantity:
		breakdown = quantity

	data_to_be_written = []
	knowledgeKeywords = []
	duplicates = []

	results, created =  webSearch.objects.get_or_create(queryText = query.strip())
	if created or force or len(results.results.all()) < quantity:
		all_results = getGoogleResults(query, quantity, news, force)
	else:
		all_results = []

	if len(all_results) == 0 and not created:
		all_results = [r.url for r in results.results.all()]

	all_results = all_results[:quantity]
	print "TOTAL RESULTS ", str(len(all_results))
	# Done with getting search results



	for index, i in enumerate(all_results):
		try:
			wr, created = WebResource.objects.get_or_create(url = i)
			if created:
  				wr = parseURL(i, True)
			data = {'url' : i}
			keywords = [w for w in count(wr.text, top = 10, stemmer = LEMMA) if w not in stop]

			if 'books.google' in i:
				text = ''
			else:
				text = wr.text

			data.update({
				'keywords' : keywords,
				'text' : plaintext(text),
				'title' : wr.title,
				'urls' : wr.urls,
				'type' : 'result',
				'index' : index+1,
				'similar' : [],
				'duplicates' : [],
				'category' : 0,
				})

			if wr not in results.results.all():
				results.results.add(wr)

			data['plaintext'] = data['text'].split('\n')

			# while '' in data['plaintext']:
			# 	data['plaintext'].remove('')

			# knowledgeKeywords.extend(data['keywords'])

			data_to_be_written.append(data)
		except Exception as e:
			print e

	print "Response Result model Prepared"

	if not analysis:
		return data_to_be_written

	list_of_sim_docs, model, m = find_similarity(data_to_be_written)
	for i in list_of_sim_docs:
		similar = {
			'type' : 'similar',
			's' : i.get('source'),
			'd' : i.get('dest'),
			'source' : i.get('source'),
			'dest' : i.get('dest'),
			'score' : i.get('score'),
		}
		data_to_be_written.append(similar)

		if similar['score'] > 0.9:
			for res in data_to_be_written:
				if res['type'] in ['result','duplicate'] and res['url'] == i.get('dest') and len(res['text'])>0:
					print "Duplicate [{0}].[{1}]".format(i['source'][:20],i['dest'][:20])
					res['type'] = 'duplicate'


	items = [Document(i.get('text'), name=i.get('url'), description=i.get('index'), stemmer = LEMMA) for i in data_to_be_written]
	m = Model(items, weight=TFIDF)
	# k = 10
	####### BEGIN Experimental Setup ##########

	# v,d = m.features, m.documents
	# y,x = len(m.documents),len(m.features)


	def build_matrix(w = None, d = None):
		y,x = len(d),len(w)
		model = np.zeros((y,x))

		for i in range(y):
			model[i] = [1 if w[j] in d[i].words else 0 for j in range(x)]

		return model

	# def find_word_matches(model, words = None, d = None):
	# 	y,x = model.shape
	# 	for i in range(y):
	# 		for j in range(i+1,y):
	# 			a = np.copy(model[i])
	# 			b = np.copy(model[j])

	# 			a_ones = np.count_nonzero(a)
	# 			b_ones = np.count_nonzero(b)

	# 			comparison = (a==b)

	# 			cross_product = a*b
	# 			intersection = np.count_nonzero(cross_product)
	# 			union = a_ones+b_ones-intersection

	# 			if a_ones+b_ones>0 and intersection > 0:
	# 				score = intersection/union
	# 			else:
	# 				score = 0

	# 			if model[i].any() and model[j].any() and comparison.any() and score > 0.4:
	# 				print "Match [{0}] {1}:[{2} words] - [{3}] {4}:[{5} words] : {6} words".format(d[i].description,d[i].name[:30], np.count_nonzero(a), d[j].description,d[j].name[:30], np.count_nonzero(b), score, math.fabs(d[i].description - d[j].description))
	# 				similar = {
	# 					'type' : 'similar',
	# 					'source' : d[i].name,
	# 					'dest' : d[j].name,
	# 					'score' : score,
	# 				}
	# 				data_to_be_written.append(similar)

	# 			if score >= 0.9:
	# 				for res in data_to_be_written:
	# 					if res['type'] in ['result','duplicate'] and res['url'] == d[j].name and len(res['text'])>0:
	# 						print "Duplicate [{0}].[{1}]".format(i+1,j+1)
	# 						res['type'] = 'duplicate'
	# 	return model

	def word_frequency(model, words = None, documents = None, threshold1 = 0, threshold2 = 1, transpose = False):
		"Returns frequent word amoung documents in range of threshold"
		y,x = model.shape
		data = {}

		for i in range(x):
			count = np.count_nonzero(model[:,i])/y
			if count >= threshold1 and count <= threshold2:
				if words:
					data[words[i]] = count
				else:
					data[i] = count
		return data

	model = build_matrix(m.features, m.documents)
	# model = find_word_matches(model, m.features, m.documents)
	knowledgeKeywords = [w for w in word_frequency(model, m.features, m.documents, 0.2, 0.8)][:20]

	####### END Experimental Setup ##########

	# c = m.cluster(method=HIERARCHICAL, k=k)
	# for i in c:
	# 	cluster = []
	# 	k = []
	# 	contains_text = False

	# 	for item in i:
	# 		for data in data_to_be_written:
	# 			if data.get('type') == 'result' and data.get('url')==item.name:
	# 				cluster.append({
	# 					'url' : data.get('url'),
	# 					'index' : item.description,
	# 					})
	# 				if data.get('text'):
	# 					k.extend([w for w in count(words(data.get('text')), top=50, stemmer = PORTER, exclude=[], stopwords=False, language='en')])
	# 					contains_text=True
	# 	cluster = {
	# 		'type' : 'cluster',
	# 		'data' : cluster,
	# 		'index' : min([c.get('index') for c in cluster] + [0]),
	# 		'keywords' : [w for w in count(k, top=10, stemmer = PORTER, exclude=[], stopwords=False, language='en')]
	# 	}

	# 	cluster['contains_text'] = contains_text

	# 	data_to_be_written.append(cluster)


	# print "{0} results".format(len(data_to_be_written))
	data_to_be_written.append({
		'type' : 'meta',
		'keywords' : knowledgeKeywords,
		})


	result = {}
	for i in data_to_be_written:
		if i.get('type') in ['result', 'duplicate']:
			url = i.get('url')
			index = int(i.get('index'))

			result[index] = [1 for r in data_to_be_written if r.get('type') == 'similar' and r['source'] == url]

	result2 = [i for i,j in result.iteritems()]
	result3 = [len(j) for i,j in result.iteritems()]
	
	Process(target=plot_graph, args=(result2, result3)).start()

	return data_to_be_written
