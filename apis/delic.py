import feedparser

def by_tag(t):
	fobj = feedparser.parse("http://del.icio.us/rss/popular/%s" % t)
	# keys in entries: ['updated', 'updated_parsed', 'links', 'author', 'title', 'title_detail', 'link', 'id', 'tags']
	return fobj['entries']
