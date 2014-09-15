#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import os
import sys
import urllib
import urllib2
import re
from bs4 import BeautifulSoup
from os import listdir
import pprint


def usage():
	print "Usage: preprocess.py [--help] --url=data_url --file=file_path --dir=dir_path --output=path --sep=separator --labels=lablel1,label2 --tag=tag1,tag2,... " 
	print ""

def parseRaw(raw, sep, labels, tags, records = []):
	for rr in raw.findAll(sep):
		r = {}
		for tag in tags:
			try:
				r[tag] = rr.find(tag).text
			except:
				continue

		for label in labels:
			try:
				r[label] = map(lambda x: getattr(x,'text'), rr.find(label).findAll('d'))		
			except:
				continue
		
		records.append(r)

	return records
	
def main():
	if len(sys.argv) < 5:
		print "ERROR: not enough arguments"
		usage()
		sys.exit()
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "l:d:f:o:u:s:t:h", ["label=", "dir=", "file=", "url=","sep=","help", "tag=", "output="]) 
	except getopt.GetoptError:           
		usage()                          
		sys.exit(2)
                     
	for opt, arg in opts:                
		if opt in ("-h", "--help"):      
			usage()                     
			sys.exit()                  
		elif opt in ("-u", "--url"): 
			url= arg
		elif opt in ("-f", "--file"): 
			file_path = arg
		elif opt in ("-d", "--dir"): 
			dir_path = arg
		elif opt in ("-o", "--output"): 
			ofile = arg
		elif opt in ("-s", "--sep"): 
			sep= arg
		elif opt in ("-l", "--label"): 
			labels= arg.split(',')
		elif opt in ("-t", "--tag"): 
			tags = arg.split(',')
		else:
			print "unhandled option"
			usage()
			sys.exit()

	if 'url' in locals():
		raw_data = BeautifulSoup(urllib2.urlopen(url), "html.parser")
		data = parseRaw(raw_data, sep, labels, tags)
	elif 'file_path' in locals():
		raw_data = BeautifulSoup(open(file_path), "html.parser")
		data = parseRaw(raw_data, sep, labels, tags)
	elif 'dir_path' in locals():
		data = []
		for f in listdir(dir_path):
			print 'Parse file ' + dir_path + '/' + f
			raw_data = BeautifulSoup(open(dir_path + '/' + f), "html.parser")
			data = parseRaw(raw_data, sep, labels, tags, data)
	else:
		print "Need to pass argument url, file, or dir"
		usage()
		sys.exit(2)
	
	pprint.PrettyPrinter(indent=4).pprint(data[1])

if __name__ == "__main__":
	main()
