# see also http://www.flickr.com/services/api/
# using flickr json feed http://www.flickr.com/services/feeds/
import urllib, simplejson
#api_key = '4b86073fd285073df5233297bd5f596b'
#flickr = flickrapi.FlickrAPI(api_key)

def by_tag(t):
	# public feed
	feed = urllib.urlopen("http://api.flickr.com/services/feeds/photos_public.gne?tags=%s&format=json&nojsoncallback=1" % t)
	jobj = simplejson.load(feed)
	# keys in items: ['description', 'date_taken', 'title', 'media', 'author', 'link', 'published', 'author_id', 'tags']
	return jobj['items']
