from django.core.management.base import BaseCommand
from app.models import *
from django.contrib.auth.models import User
from django.db.models import Q
import operator
class Command(BaseCommand):
	def handle(self, *args, **options):
		try:
			import nltk
			nltk.download('stopwords')
			nltk.download('maxent_treebank_pos_tagger')
			nltk.download('punkt')
		except:
			pass
