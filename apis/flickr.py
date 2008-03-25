# see also http://www.flickr.com/services/api/
# using flickr json feed http://www.flickr.com/services/feeds/
import urllib, simplejson, util
#api_key = '4b86073fd285073df5233297bd5f596b'
#flickr = flickrapi.FlickrAPI(api_key)

mark = 0

def by_tag(t):
	global mark
	mark = util.pause('flickr', mark)
	# public feed
	feed = urllib.urlopen(u"http://api.flickr.com/services/feeds/photos_public.gne?tags=%s&format=json&nojsoncallback=1" % unicode(t))
	jobj = simplejson.load(feed)
	# keys in items: ['description', 'date_taken', 'title', 'media', 'author', 'link', 'published', 'author_id', 'tags']
	return jobj['items']

def social_network(uid):
	global mark
	mark = util.pause('flickr', mark)
	feed = urllib.urlopen("http://api.flickr.com/services/feeds/photos_friends.gne?user_id=%s&format=json&nojsoncallback=1" % uid)
	jobj = simplejson.load(feed)
	# keys in items : ["title",  "link", "media", "date_taken", "description", "published", "author", "author_id", "tags"]
	return jobj['items']

def user_images(uid):
	global mark
	mark = util.pause('flickr', mark)
	feed = urllib.urlopen("http://api.flickr.com/services/feeds/photos_public.gne?id=%s&format=json&nojsoncallback=1" % uid)
	jobj = simplejson.load(feed)
	# keys in items : ["title",  "link", "media", "date_taken", "description", "published", "author", "author_id", "tags"]
	return jobj['items']
