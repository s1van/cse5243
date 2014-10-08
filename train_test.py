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
import importlib
import time

from bs4 import BeautifulSoup
from os import listdir
from collections import Counter
from itertools import tee, islice, izip
from nltk.stem import *
from tools import parseRaw, readWordList, _ngrams, ngrams

def usage():
	print "Usage: train_test.py [--help] --file=file_path --label=label --percent=percentage --method=method --args=model_arguments" 
	print ""
	print "file       pickle data file, which is a list of dictionaries, where each has the format 'feature':list, label1:list,...'"
	print "label      class labels"
	print "percent    percentage of data used for training"
	print "method     methods like knn which can be found in method.py"
	print "args       parameters for the model"
	print ""


def main():
	if len(sys.argv) < 5:
		print "ERROR: not enough arguments"
		usage()
		sys.exit()
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "a:m:f:l:p:h", ["args=", "method=", "label=", "file=", "help", "percent="]) 
	except getopt.GetoptError:           
		usage()                          
		sys.exit(2)
                
	# init
	params = []     

	for opt, arg in opts:                
		if opt in ("-h", "--help"):      
			usage()                     
			sys.exit()                  
		elif opt in ("-f", "--file"): 
			data = pickle.load(open(arg, "rb"))
		elif opt in ("-l", "--label"): 
			label = arg
		elif opt in ("-a", "--args"): 
			params = arg.split(',')
		elif opt in ("-p", "--percent"): 
			p = int(arg)
		elif opt in ("-m", "--method"): 
			method = importlib.import_module(arg)
		else:
			print "unhandled option"
			usage()
			sys.exit()

	print 'Start to train the model ...' 
	ts = time.time()
	train_set_size = int(len(data) * p/100)
	model = method.train(data[0: train_set_size], label)
	stat = Counter()
	te = time.time()
	print 'Training takes', te-ts, 'sec', 'with #examples =', train_set_size
	print ''

	print 'Start to test the model ...'
	ts = time.time()
	for r in data[train_set_size:len(data)]:
		c = method.test(model, r, label, params)
		if set(c).intersection(r[label]):
			stat['correct'] += 1
		else:
			stat['incorrect'] += 1
	te = time.time()
	print 'Testing takes', te-ts, 'sec', 'with #samples =', len(data) - train_set_size
	print 'Time to classify a tuple', (te-ts)/(len(data) - train_set_size)
	print ''

	print 'Result:'
	pprint.pprint(stat)
	acc = stat['correct'] / float(stat['correct'] + stat['incorrect'])
	print 'Accuracy =', acc

if __name__ == "__main__":
	main()
