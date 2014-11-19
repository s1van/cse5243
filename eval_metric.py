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

from os import listdir
from collections import Counter
from itertools import tee, islice, izip
from nltk.stem import *
from tools import jaccard_similarity, jaccard_similarity_1d

def usage():
	print "Usage: eval_metric.py [--help] --file=file_path --method=method --args=method_arguments" 
	print ""
	print "file       pickle data file, which is a list of dictionaries, where each has the format 'feature':list, label1:list,...'"
	print "method     methods like min_hash which can be found in method.py"
	print "args       parameters for the method"
	print ""


def main():
	if len(sys.argv) < 2:
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
			data = pickle.load(open(arg, "rb"))
		elif opt in ("-a", "--args"): 
			params = arg.split(',')
		elif opt in ("-m", "--method"): 
			method = importlib.import_module(arg)
		else:
			print "unhandled option"
			usage()
			sys.exit()

	print 'Preprocess Data ...' 
	ts = time.time()
	pnum = len(data)
	raw_data_points = [item['feature'] for item in data]
	# Get unique features in data
	fdict = {}
	fid = 0
	for fv in raw_data_points:
		for f in fv:
			if f not in fdict:
				fdict[f] = fid
				fid += 1
	
	# Generate compact feature vector
	#data_points = [sorted([fdict[f] for f in vec]) for vec in raw_data_points]
	data_points = [set([fdict[f] for f in vec]) for vec in raw_data_points]
	#data_points = [set(item['feature']) for item in data]

	# free memory space
	data = raw_data_points = [] 
	te = time.time()
	print 'Preprocessing takes', te-ts, 'sec', 'with #data_point =', pnum, len(fdict)
	print ''


	print 'Calculate the baseline ... (Jaccard Similarity)'
	base_scores = np.ones((pnum, pnum))
	ts = time.time()
	for i in range(pnum):
		for j in range(i):
			base_scores[j,i] = base_scores[i,j] = jaccard_similarity(data_points[i], data_points[j]) # still faster
			#base_scores[j,i] = base_scores[i,j] = jaccard_similarity_1d(data_points[i], data_points[j])
	te = time.time()
	print 'Calculation takes', te-ts, 'sec' 
	# print base_scores
	print ''


	print 'Evaluate Method ...' 
	ts = time.time()
	pdata = method.process(data_points, fdict.values(), params)
	te = time.time()
	print 'Data Processing takes', te-ts, 'sec' 
	ts = time.time()
	scores = method.evaluate(pdata)
	te = time.time()
	print 'Evaluation takes', te-ts, 'sec' 
	# print scores
	print ''
	
	mse = np.mean(np.square(base_scores - scores))
	print 'Method Mean Squared Error = ', mse, '(Param=', params, ')' 
	rme = np.mean(np.abs(base_scores - scores) / (np.maximum(base_scores, np.ones(base_scores.shape)*1e-6 )) )
	print 'Method Mean Squared Error = ', rme, '(Param=', params, ')' 
	


if __name__ == "__main__":
	main()
