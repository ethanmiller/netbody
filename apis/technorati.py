import feedparser

def by_tag(t):
	fobj = feedparser.parse("http://feeds.technorati.com/tag/%s" % t)
	# keys in entries: ['updated', 'updated_parsed', 'links', 'title', 'summary_detail', 'comments', 'summary', 'tapi_inboundblogs', 'guidislink', 'title_detail', 'link', 'tapi_inboundlinks', 'tapi_linkcreated', 'id']
	return fobj['entries']
