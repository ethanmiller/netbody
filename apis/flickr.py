# see also http://www.flickr.com/services/api/
# using flickr json feed http://www.flickr.com/services/feeds/
import urllib, simplejson, util
#api_key = '4b86073fd285073df5233297bd5f596b'
#flickr = flickrapi.FlickrAPI(api_key)

mark = 0

def by_tag(t):
	global mark
	mark = util.pause('flickr', mark)
	t = util.unicode_enforce(t)
	# public feed
	try:
		feed = urllib.urlopen("http://api.flickr.com/services/feeds/photos_public.gne?tags=%s&format=json&nojsoncallback=1" % t.encode("utf-8"))
	except IOError:
		print "{{ socket timeout for flickr by_tag"
		return []

	try:
		jobj = simplejson.load(feed)
	except ValueError:
		print "{{ json escape err?" # I think this is some kind of formatting err in returned json
		return []
	# keys in items: ['description', 'date_taken', 'title', 'media', 'author', 'link', 'published', 'author_id', 'tags']
	return jobj['items']

def social_network(uid):
	global mark
	mark = util.pause('flickr', mark)
	try:
		feed = urllib.urlopen("http://api.flickr.com/services/feeds/photos_friends.gne?user_id=%s&format=json&nojsoncallback=1" % uid)
	except IOError:
		print "{{ socket timeout for flickr social_network"
		return []
	try:
		jobj = simplejson.load(feed)
	except ValueError:
		print "{{ json escape err?" # I think this is some kind of formatting err in returned json
		return []
	# keys in items : ["title",  "link", "media", "date_taken", "description", "published", "author", "author_id", "tags"]
	return jobj['items']

def user_images(uid):
	global mark
	mark = util.pause('flickr', mark)
	try:
		feed = urllib.urlopen("http://api.flickr.com/services/feeds/photos_public.gne?id=%s&format=json&nojsoncallback=1" % uid)
	except IOError:
		print "{{ socket timeout for flickr user_images"
		return []
	try:
		jobj = simplejson.load(feed)
	except ValueError:
		print "{{ json escape err?" # I think this is some kind of formatting err in returned json
		return []
	# keys in items : ["title",  "link", "media", "date_taken", "description", "published", "author", "author_id", "tags"]
	return jobj['items']

def check_for_user(uname):
	""" return a flickr user id if it exists """
	from BeautifulSoup import BeautifulSoup
	global mark
	mark = util.pause('flickr', mark)
	try:
		page = urllib.urlopen("http://flickr.com/photos/%s" % uname)
	except IOError:
		print "{{ socket timeout for flickr user_images"
		return None
	soup = BeautifulSoup(page.read())
	inp = soup.findAll("input", attrs={"name" : "w"})
	fid = inp[0]["value"]
	if fid == "all" : return None
	print "^^ found a flickr usr %s" % uname
	return fid
	
