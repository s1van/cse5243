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
import numpy as np

from collections import Counter

def process(vecs, farray, params):
	k = int(params[0])
	minhashed = [[] for vec in vecs]
#	minhashed = [np.ones(k) for vec in vecs]

	for r in range(k):
		pm = np.random.permutation(len(farray))
#		pfarray = [farray[i] for i in pm]
		for i in range(len(vecs) ):
#			first = len(pm)
#			for f in vecs[i]:
#				offset = pfarray.index(f)
#				if (offset < first ):
#					minhashed[i][r] = f
#					first = offset
			for index in pm:
				if farray[index] in vecs[i]:
					minhashed[i].append(farray[index])
					break

	return [np.array(vec) for vec in minhashed]
#	return minhashed

def evaluate(hvecs):
	num = len(hvecs)
	scores = np.ones((num, num))
	for i in range(num):
		x = hvecs[i]
		for j in range(i):
			y = hvecs[j]
			shared = float(len(x[x==y]))
			scores[i,j] = scores[j,i] = shared / (len(x) + len(y) - shared)
	return scores
