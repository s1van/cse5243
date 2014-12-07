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
import operator

from collections import Counter
import numpy as np
import itertools as it


def test(model, r, label, params):
	rules = model["rules"] 
	index = model["index"]
	retc = []

	fset = set([e[0] for e in r['feature']])
	for left in index:
		 if left.issubset(fset):
			retc.append(rules[left][0])

	return retc

def train(data, label, params):
	ntx = len(data)
	support = int(float(params[0]) * ntx)
	confidence = float(params[1])

	# Return list of rules [left -> (right, confidence)] 
	rules = {}

	# Each transaction contains both the features and labels
	txs = [set([e[0] for e in r['feature']] + r[label]) for r in data]
	# Get all labels
	ls = set([l for r in data for l in r[label]])
	
	lis = {} # Large Item Sets
	cc = {} # Candidate Counter Dictionary
	parents = {} # tell for a given large item set, who are its parents

	# Get 1-item large item set
	cc[1] = counters = Counter()
	for tx in txs:
		for item in tx:
			counters[frozenset([item])] = 0
	for tx in txs:
		for item in tx:
			counters[frozenset([item])] += 1
	lis[1] = [k for k,v in counters.items() if v >= support]

	i = 1
	while (len(lis[i]) > 0):
		items = lis[i]
		itemsets = set(items)
		i = i + 1 # number of items for qualified item set
		candidates = set()
		# Generate all i-length candidate item sets
		for j in range(len(items)):
			for k in range(j):
				c = items[j].union(items[k]) # potential new candidate	
				if c in candidates:
					continue
				if (len(c) == i):	# size is increased by one
					# pruning
					skip = False
					for c_1 in it.combinations(c, i-1):
						if set(c_1) not in itemsets:
							skip = True
							break
					if (skip):
						continue	
					candidates.add(c)
					parents[c] = (items[j], items[k])

		cc[i] = counters = Counter()
		for c in candidates:
			counters[c] = 0	
			for tx in txs:
				if c.issubset(tx):
					counters[c] += 1	
		# Get new large item sets
		lis[i] = [c for c in candidates if counters[c] >= support]
			
	largest_is_size = i - 1
	# Generate new rules from lis[2:]
	for i in range(2, largest_is_size + 1):
		for itemset in lis[i]:
			clabels = itemset.intersection(ls)
			left = itemset.difference(ls)
			if (len(left) == 0):
				continue
			for lab in clabels:
				conf = ((float)(cc[i][itemset])) /cc[len(left)+1][left.union(set([lab]))]
				if (conf >= confidence ):
					if left in rules:
						if rules[left][1] > conf:
							continue
					rules[left] = (lab, conf)
	
	index = [left for left,label in sorted([(k,v[1]) for k,v in rules.items()], key=operator.itemgetter(1), reverse=True)]
					

	return {"rules": rules, "index": index}
