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
from sklearn.cluster import DBSCAN


def fit(fvecs, params):
	eps_ = int(params[0])
	min_s = int(params[1])
	metric_=params[2]
	# affinity : “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, or ‘precomputed’

	model = DBSCAN(eps=eps_, min_samples=min_s, metric=metric_)
	model.fit(fvecs)
	print len(set(model.labels_))
	return model.labels_

