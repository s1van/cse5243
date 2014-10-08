#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import os, io
import sys
import urllib
import urllib2
import re
import pprint
import pickle

from bs4 import BeautifulSoup
from os import listdir
from collections import Counter
from itertools import tee, islice, izip
from nltk.stem import *


def parseRaw(raw, sep, labels, tags, records = []):
	for rr in raw.findAll(sep):
		r = {}
		for tag in tags:
			try:
				r[tag] = BeautifulSoup(rr.find(tag).text).text	# to interpret special symbols properly
			except:
				continue

		for label in labels:
			try:
				r[label] = map(lambda x: getattr(x,'text'), rr.find(label).findAll('d'))		
			except:
				continue
		
		records.append(r)

	return records
	
def readWordList(words_file):
	open_file = open(words_file, 'r')
    	words_list = set()
	contents = open_file.readlines()
	for i in range(len(contents)):
     		words_list.add(contents[i].strip('\n'))
	return words_list    

stemmer = PorterStemmer()
def _ngrams(lst, n, stoplist, stem):
	global stemmer 
	tlst = lst
	while True:
		a, b = tee(tlst)
		# convert strings to lowercase
		l = map(lambda s:s.lower(), tuple(islice(a, n)))

		# handle stop list
		skip = False
		for e in l:
			if e in stoplist or re.match('[0-9]+', e):
				next(b)
				tlst = b
				skip = True
				break
		if skip:
			continue

		# generate ngram
		if len(l) == n:
			if stem:
				# stemming
				yield tuple(map(stemmer.stem, l))
			else:
				yield l
			next(b)
			tlst = b
		else:
			break

def ngrams(text, n, stoplist = [], stem = True):
	lst = re.findall("\w+", text)
	return Counter(_ngrams(lst, n, stoplist, stem) )


