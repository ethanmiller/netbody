import feedparser

mark = 0

def by_tag(t):
	pause()
	fobj = feedparser.parse("http://feeds.technorati.com/tag/%s" % t)
	# keys in entries: ['updated', 'updated_parsed', 'links', 'title', 'summary_detail', 'comments', 'summary', 'tapi_inboundblogs', 'guidislink', 'title_detail', 'link', 'tapi_inboundlinks', 'tapi_linkcreated', 'id']
	return fobj['entries']

def pause():
	global mark
	import time, util
	elapsed = time.clock() - mark
	if elapsed < util.CONST.SERVICE_HIT_PAUSE:
		print ".... pausing for flickr ...."
		time.sleep(util.CONST.SERVICE_HIT_PAUSE - elapsed)
	mark = time.clock()
