from __future__ import unicode_literals

from django.db import models

features = (
	('0','title'),
	('1','content'),
	)

structural_tags = (
	('0','title'),
	('1','document'),
	('2','content'),
	('3','reference'),
	)

##### Old Models #####
class link(models.Model):
	url = models.TextField(blank = True)
	title = models.TextField(blank = True)
	text = models.TextField(blank = True)
	keywords = models.TextField(blank = True)
	structuralCandidates = models.ManyToManyField('structuralCandidates', related_name = "struct")

class wordCandidate(models.Model):
	text = models.TextField()
	feature = models.TextField()

class contextualCandidates(models.Model):
	# order = models.IntegerField(default = 0)
	feature = models.CharField(max_length = 20, choices=features)
	text = models.TextField(blank = True)
	wordCandidates = models.ManyToManyField('wordCandidate', related_name = "contexts")

class structuralCandidates(models.Model):
	tag = models.CharField(max_length = 2, choices = structural_tags, default = "2")
	# order = models.IntegerField(default = 0)

	contextualCandidates = models.ManyToManyField('contextualCandidates', related_name = "struct")


######################new models################################33


WebResourceChoices = (
	('0','url'),
	('1','document/attachment'))

class webSearch(models.Model):
	queryText = models.CharField(max_length = 100)
	results = models.ManyToManyField('WebResource')

class WebResource(models.Model):
	resourceType = models.CharField(max_length = 100, default = "0", choices = WebResourceChoices)
	url = models.TextField(blank = True)
	text = models.TextField(blank = True)
	# plaintext = models.TextField(blank = True)
	# normalised_text = models.TextField(blank = True)
	keywords = models.TextField(blank = True)
	title = models.CharField(max_length = 500, blank = True)
	urls = models.TextField(blank = True)





	












