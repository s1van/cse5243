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
import numpy as np

from bs4 import BeautifulSoup
from os import listdir
from collections import Counter
from itertools import tee, islice, izip
from nltk.stem import *
from tools import parseRaw, readWordList, _ngrams, ngrams
from scipy.stats import entropy

def usage():
	print "Usage: cluster_test.py [--help] --file=file_path --method=method --args=model_arguments" 
	print ""
	print "file       pickle data file, which is a list of dictionaries, where each has the format 'feature':list, label1:list,...'"
	print "method     methods like knn which can be found in method.py"
	print "args       parameters for the model"
	print ""


def calculate_entropy(cnum, labels, clusters):
	enum = len(clusters)
	epy = 0
	for c in range(0, cnum):
		subl = labels[clusters == c]
		subc = Counter(subl)
		epy = epy + entropy(subc.values()) * len(subl) / enum
	return epy
	
def calculate_variance(clusters):
	return np.var(Counter(clusters).values())
	

def main():
	if len(sys.argv) < 3:
		print "ERROR: not enough arguments"
		usage()
		sys.exit()
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "a:m:f:h", ["args=", "method=", "file=", "help"]) 
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
			print 'Loading ...' 
			data = pickle.load( open(arg, "rb"))
			fvecs = data['feature_vector']
			labels = data['label']
			label_names = data['all_label']
		elif opt in ("-a", "--args"): 
			params = arg.split(',')
		elif opt in ("-m", "--method"): 
			method = importlib.import_module(arg)
		else:
			print "unhandled option"
			usage()
			sys.exit()

	print 'Start Clustering ...' 
	ts = time.time()
	clustered = method.fit(fvecs, params)
	te = time.time()
	print 'Clustering takes', te - ts, 'sec'
	print ''

	cnum = max(clustered) + 1
	print 'Evaluate Clustering Result ...'
	slabels = np.array([str(lab) for lab in labels])
	cl = Counter(slabels)
	e_score1 = entropy(cl.values()) # original
	e_score2 = calculate_entropy(cnum, slabels, clustered) # new
	print 'Entropy Score =', e_score1, e_score2, e_score1 - e_score2
	print ''

	va = calculate_variance(clustered)
	print 'Clustering Variance =', va
	print Counter(clustered)

if __name__ == "__main__":
	main()
