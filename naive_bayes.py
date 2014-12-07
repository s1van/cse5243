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

from collections import Counter


def test(model, r, label, params):
	retc = []

	feature_dist = model['fdist']
	class_dist = model['cdist']
	absence_penalty = float(1) / class_dist.most_common()[0][1]
	
	scores = Counter()
	for c in class_dist:
		scores[c] = float(1)
		used = 0
		for f in r['feature']:
			if (feature_dist[c][f] > 0):
				used += 1
				scores[c] = scores[c] * float(feature_dist[c][f]) / class_dist[c]
			else:
				scores[c] = scores[c] * absence_penalty

		scores[c] = scores[c] * used / len(r['feature']) # scale the file score according to #feature used
	retc.append(scores.most_common()[0][0])
	return retc

def train(data, label, params):
	feature_dist = dict()
	class_dist = Counter()

	for r in data:
		for c in r[label]:
			class_dist[c] += 1
	for c in class_dist:
		feature_dist[c] = Counter()

	for r in data:
		for c in r[label]:
			for f in r['feature']:
				feature_dist[c][f] += 1
	return {'fdist':feature_dist, 'cdist':class_dist}
