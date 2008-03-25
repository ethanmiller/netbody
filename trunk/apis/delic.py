import feedparser, util

mark = 0

def by_tag(t):
	global mark
	mark = util.pause("del.icio.us", mark)
	fobj = feedparser.parse(u"http://del.icio.us/rss/popular/%s" % unicode(t))
	# keys in entries: ['updated', 'updated_parsed', 'links', 'author', 'title', 'title_detail', 'link', 'id', 'tags']
	return fobj['entries']

def url_data(url):
	global mark
	mark = util.pause("del.icio.us", mark)
	fobj = feedparser.parse(url_feed(url))
	# username is entries['author'], for tags entries['tags'] =  [{'term': 'tag othertag', 'scheme': None, 'label': None}]
	return fobj['entries']

def social_network(uname):
	global mark
	mark = util.pause("del.icio.us", mark)
	fobj = feedparser.parse("http://feeds.delicious.com/rss/network/%s" % uname)
	# entries are from social network, but there may be multiple posts from same members of network
	ret = []
	for e in fobj['entries']:
		a = e.get('author', None)
		if a not in ret and a != None: ret.append(e['author'])
	return ret

def links(uname):
	global mark
	mark = util.pause("del.icio.us", mark)
	fobj = feedparser.parse("http://feeds.delicious.com/rss/%s" % uname)
	# keys in entries : ['summary_detail', 'rdf_bag', 'updated_parsed', 'links', 'title', 'author', 'rdf_li', 'updated', 'taxo_topics', 'summary', 'title_detail', 'link', 'id', 'tags']
	return fobj['entries']

def url_feed(url):
	import hashlib
	m = hashlib.md5()
	m.update(url)
	return "http://feeds.delicious.com/rss/url/%s" % m.hexdigest()

