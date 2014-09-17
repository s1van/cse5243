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


def usage():
	print "Usage: preprocess.py [--help] --url=data_url --file=file_path --dir=dir_path --output=path --sep=separator --label=lablel1,label2 --tag=tag1,tag2,... " 
	print "                              --stoplist=file --MIN=percentage1,pecentage2,..."
	print ""
	print "sep        token used to identify an article, e.g. <reuters> article </reuters>"
	print "tag        tag specifies the content segment in one article, e.g. <reuters> <content> Content </content> </reuters>"
	print "stoplist   path of the file that contains stop words"
	print "MIN        filter out low frequent words (phrases) that contribute to MIN portion of total word (phrase) appearances"
	print "           with percentage1 corresponding to 1-gram, percentage2 corresponding to 2-gram, ..."
	print "output     result will be saved to output, and selected features will be dumped to file output.feature"
	print ""
	print "Example: ./preprocess.py --dir=/tmp/data --sep=reuters --label=topics,places --tag=body --stoplist=/tmp/stoplist --MIN=95 --output=/tmp/out.pickle"

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

def selectFeatures(data, tags, stoplist, p):
	features = set()
	# get n-gram statistics
	stat = {}

	cbuf = Counter()
	cbuf_size = 0
	for num in range(1, len(p) + 1):	# n-gram lengthes
		stat[num] = Counter()
		for tag in tags:
			stat[(tag, num)] = Counter()
			for r in data:
				try:
					cbuf += ngrams(r[tag], num, stoplist)
					cbuf_size += 1
					if cbuf_size > 64:
						stat[(tag, num)] += cbuf
						cbuf = Counter()
						cbuf_size = 0
				except KeyError:
					continue
			if cbuf_size > 0:
				stat[(tag, num)] += cbuf
				cbuf = Counter()
				cbuf_size = 0

			stat[num] += stat[(tag, num)]

		# generate the counter value distribution
		dist = {}
		for v in stat[num].values():
			try:
				dist[v] += 1
			except:
				dist[v] = 1

		# choose minimum frequency accordingly
		s = sum([k*v for k,v in zip(dist.keys(), dist.values()) ])
		c = minfreq = 0
		for k in dist.keys():
			c += dist[k] * k
			if (c > s * p[num - 1] / 100):
				minfreq = k
				break

		cfilter(stat[num], minfreq, sys.maxint)
		features = features.union(stat[num].keys() )
	return features

def extractFeatures(data, features, tags, stoplist, n):
	for tag in tags:
		for r in data:
			r['feature'] = {}
			for num in range(1, n + 1):	# n-gram lengthes
				try:
					c = ngrams(r[tag], num, stoplist)
					for f in c:
						if f in features:
							r['feature'][f] = c[f]
				except KeyError:
					continue
	
	return data

def main():
	if len(sys.argv) < 5:
		print "ERROR: not enough arguments"
		usage()
		sys.exit()
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "l:d:f:o:u:s:t:S:M:h", ["label=", "dir=", "file=", "url=","sep=","help", "tag=", "output=", "stoplist=", "MIN="]) 
	except getopt.GetoptError:           
		usage()                          
		sys.exit(2)
                     
	# init vars
	stoplist = set()
	minfreq_p = [0];

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
		elif opt in ("-M", "--MIN"): 
			minfreq_p = map(int, arg.split(','))
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

	print 'Select features ...'
	features = selectFeatures(data, tags, stoplist, minfreq_p)
	print '#feature = ', len(features) 

	print 'Extract features ...'
	data = extractFeatures(data, features, tags, stoplist, len(minfreq_p))

	# output
	if 'ofile' in locals():
		with io.open(ofile, 'wb') as f:
			pickle.dump(data, f)
			print "Save result to ", ofile
		with io.open(ofile + '.feature', 'wb') as f:
			print >> f, features
			print "Save feature to ", ofile + '.feature'


if __name__ == "__main__":
	main()
