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
from tools import parseRaw, readWordList, _ngrams, ngrams

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

def cfilter(counter, MIN, MAX):
	keys = counter.keys()
	for k in keys:
		if counter[k] < MIN or counter[k] > MAX:
			del counter[k]
	return counter

def cpfilter(counter, pmin, pmax):
	s = sum(counter.values() )
	minfreq = int(s * pmin / 100)
	maxfreq = int(s * pmax / 100)
	return cfilter(counter, minfreq, maxfreq)

def csfilter(counter, MIN, MAX): # drop top %MAX and bottom %MIN items
	keys = counter.keys()
	drop_max = int(len(keys) * MAX / 100)
	drop_min = int(len(keys) * MIN / 100)
	nc = counter.most_common() # list type
	del nc[0 : drop_max]
	del nc[-drop_min: -1]
	return nc

def selectFeatures(data, tags, stoplist, p):	# p[i] for i-gram passing high pass filter

	dlist = []
	for r in data:
		r['feature']  = []
		for num in range(1, len(p) + 1):	# n-gram lengthes
			stat = Counter()
			for tag in tags:
				try:
					stat += ngrams(r[tag], num, stoplist)
				except KeyError:
					continue
			nc = csfilter(stat, p[num - 1], 0)
			r['feature'] += [k for k,v in nc]
		if not r['feature']:
			dlist.append(r)
		
	for r in dlist:
		data.remove(r)

def cleanup(data, tags, labels):
	for tag in tags:
		for r in data:
			del r[tag]
	
	dlist = []
	for r in data:
		for label in labels:
			if not r[label]:
				dlist.append(r)
				break

	for r in dlist:
		data.remove(r)
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
	selectFeatures(data, tags, stoplist, minfreq_p)
	print 'Clean dataset ...'
	cleanup(data, tags, labels)

	# output
	if 'ofile' in locals():
		with io.open(ofile, 'wb') as f:
			pickle.dump(data, f)
			print "Save result to ", ofile
		with io.open(ofile + '.io', 'wb') as f:
			pprint.pprint(data, f)
			print "Save feature to ", ofile + '.io'


if __name__ == "__main__":
	main()
