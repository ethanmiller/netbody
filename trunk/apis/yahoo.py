# File: YahooTermExtraction.py
#
# An interface to Yahoo's Term Extraction service:
#
# http://developer.yahoo.net/search/content/V1/termExtraction.html
#
# "The Term Extraction Web Service provides a list of significant
# words or phrases extracted from a larger content."
#

import urllib, util
from xml.etree import ElementTree

mark = 0
URI = "http://api.search.yahoo.com"
URI = URI + "/ContentAnalysisService/V1/termExtraction"
APPID = "kQqLnvnV34Gkbc2i38FY5ghCD_1Mi_auohTsoSIimq5ORhSI0.FWFXkj8I57"

def termExtraction(context, query=None):
	global mark
	mark = util.pause("yahoo", mark)
	d = dict( appid=APPID, context=context.encode("utf-8"))
	if query:
		d["query"] = query.encode("utf-8")
	result = []
	f = urllib.urlopen(URI, urllib.urlencode(d))
	for event, elem in ElementTree.iterparse(f):
		if elem.tag == "{urn:yahoo:cate}Result":
			result.append(elem.text)
	return result
