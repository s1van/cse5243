#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import os
import sys
import urllib
import urllib2
import re
import pprint

from bs4 import BeautifulSoup
from os import listdir
from collections import Counter
from itertools import tee, islice, izip
from nltk.stem import *


def usage():
	print "Usage: preprocess.py [--help] --url=data_url --file=file_path --dir=dir_path --output=path --sep=separator --labels=lablel1,label2 --tag=tag1,tag2,... " 
	print ""

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

def cfilter(counter, MIN, MAX):
	keys = counter.keys()
	for k in keys:
		if counter[k] < MIN or counter[k] > MAX:
			del counter[k]

def selectFeatures(data, tags, stoplist, minfreq):
	features = []
	# get n-gram statistics
	stat = {}
	for tag in tags:
		for num in range(1, 3):	# n-gram lengthes
			stat[(tag, num)] = Counter()
			for r in data:
				try:
					stat[(tag, num)] += ngrams(r[tag], num, stoplist)
				except KeyError:
					continue
			cfilter(stat[(tag, num)], minfreq, sys.maxint)
			features += stat[(tag, num)].keys()
	# collect features
	return features

def main():
	if len(sys.argv) < 5:
		print "ERROR: not enough arguments"
		usage()
		sys.exit()
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "l:d:f:o:u:s:t:S:m:h", ["label=", "dir=", "file=", "url=","sep=","help", "tag=", "output=", "stoplist=", "min_frequency="]) 
	except getopt.GetoptError:           
		usage()                          
		sys.exit(2)
                     
	# init vars
	stoplist = set()
	minfreq	= 1;

	for opt, arg in opts:                
		if opt in ("-h", "--help"):      
			usage()                     
			sys.exit()                  
		elif opt in ("-u", "--url"): 
			url= arg
		elif opt in ("-f", "--file"): 
			file_path = arg
		elif opt in ("-d", "--dir"): 
			dir_path = arg
		elif opt in ("-o", "--output"): 
			ofile = arg
		elif opt in ("-s", "--sep"): 
			sep = arg
		elif opt in ("-S", "--stoplist"): 
			stoplist = readWordList(arg)
		elif opt in ("-l", "--label"): 
			labels = arg.split(',')
		elif opt in ("-t", "--tag"): 
			tags = arg.split(',')
		elif opt in ("-m", "--min_frequency"): 
			minfreq = int(arg)
		else:
			print "unhandled option"
			usage()
			sys.exit()

	# parse the raw xml file
	if 'url' in locals():
		raw_data = BeautifulSoup(urllib2.urlopen(url), "html.parser")
		data = parseRaw(raw_data, sep, labels, tags)
	elif 'file_path' in locals():
		raw_data = BeautifulSoup(open(file_path), "html.parser")
		data = parseRaw(raw_data, sep, labels, tags)
	elif 'dir_path' in locals():
		data = []
		for f in listdir(dir_path):
			print 'Parse file ' + dir_path + '/' + f
			raw_data = BeautifulSoup(open(dir_path + '/' + f), "html.parser")
			data = parseRaw(raw_data, sep, labels, tags, data)
	else:
		print "Need to pass argument url, file, or dir"
		usage()
		sys.exit(2)

	# features involving a word form the stoplist will be removed
	print selectFeatures(data, tags, stoplist, minfreq)
	
	#pprint.PrettyPrinter(indent=4).pprint(data[1])
	#pprint.PrettyPrinter(indent=4).pprint(stoplist)

if __name__ == "__main__":
	main()
