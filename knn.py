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

def vecsim(mf,f):
	if (len(mf) < len(f)):
		return len(set(mf).intersection(f))
	else:
		return len(set(f).intersection(mf))


def test(model, r, label, params):
	np = int(params[0]) # %np percent nearest neighbour

	retc = []
	f = r['feature']
	stat = Counter()

	for i in range(0, len(model)):
		mf = model[i]['feature']
		stat[i] = vecsim(mf, f) 

	cs = Counter() # class statistics
	nr = int(len(stat) * np/100) + 1
	for pos,sim in stat.most_common():
		for c in model[pos][label]:
			cs[c] += 1 
		nr -= 1
		if (nr < 0):
			break

	retc.append(cs.most_common()[0][0])
	return retc

def train(data, label):
	return data
