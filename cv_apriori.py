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
import numpy as np

from train_test import train_test as tt

def usage():
	print "Usage: cv_apriori.py [--help] --file=file_path --label=label --percent=percentage --args1=a1,a2,a3,... --args2=b1,b2,..." 
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
		opts, args = getopt.getopt(sys.argv[1:], "a:b:m:f:l:p:h", ["args1=", "args2=", "method=", "label=", "file=", "help", "percent="]) 
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
		elif opt in ("-a", "--args1"): 
			supports= arg.split(',')
		elif opt in ("-b", "--args2"): 
			confs= arg.split(',')
		elif opt in ("-p", "--percent"): 
			p = int(arg)
		elif opt in ("-m", "--method"): 
			method = importlib.import_module(arg)
		else:
			print "unhandled option"
			usage()
			sys.exit()


	accs = np.zeros((len(supports), len(confs)))
	train_ts = np.zeros((len(supports), len(confs)))
	test_ts = np.zeros((len(supports), len(confs)))

	for i in range(len(supports)):
		for j in range(len(confs)):
			s = supports[i]
			c = confs[j]
			train_ts[i,j], test_ts[i,j], accs[i,j]   = tt(data, label, [s, c], p, method)

	print 'Supports'
	print supports

	print 'Confidences'
	print confs

	print 'Train Time'
	print train_ts
	print 'Test Time'
	print test_ts
	print 'Accuracy'
	print accs

if __name__ == "__main__":
	main()
