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
from sklearn.cluster import AgglomerativeClustering


def fit(fvecs, params):
	ncluster = int(params[0])
	# linkage : {“ward”, “complete”, “average”}
	linkage_ = params[1]
	# affinity : “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, or ‘precomputed’
	# metric = params[2]

	model = AgglomerativeClustering(n_clusters=ncluster, linkage=linkage_, affinity='manhattan')
	model.fit(fvecs)
	return model.labels_

