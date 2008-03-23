import feedparser

mark = 0

def by_tag(t):
	pause()
	fobj = feedparser.parse("http://del.icio.us/rss/popular/%s" % t)
	# keys in entries: ['updated', 'updated_parsed', 'links', 'author', 'title', 'title_detail', 'link', 'id', 'tags']
	return fobj['entries']

def url_data(url):
	pause()
	fobj = feedparser.parse(url_feed(url))
	# username is entries['author'], for tags entries['tags'] =  [{'term': 'tag othertag', 'scheme': None, 'label': None}]
	return fobj['entries']

def url_feed(url):
	import hashlib
	m = hashlib.md5()
	m.update(url)
	return "http://feeds.delicious.com/rss/url/%s" % m.hexdigest()

def pause():
	global mark
	import time, util
	elapsed = time.clock() - mark
	if elapsed < util.CONST.SERVICE_HIT_PAUSE:
		sleeptime = util.CONST.SERVICE_HIT_PAUSE - elapsed
		print ".... pausing %s seconds for del.icio.us ...."
		time.sleep(sleeptime)
	mark = time.clock()

#>>> import hashlib
#>>> m = hashlib.md5()
#>>> m.update("http://www.donotreply.com/")
#>>> m.digest()
#'gi\x10\xd4\x1a\x8e\xe5\xe0\x1b\x02\xe9E\xe02\xe9^'
#>>> m.hexdigest()
#'676910d41a8ee5e01b02e945e032e95e'
