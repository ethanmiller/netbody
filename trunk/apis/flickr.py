# using flickrapi from http://flickrapi.sourceforge.net/
# using flickr json feed http://www.flickr.com/services/feeds/
import urllib, simplejson, util, flickrapi, os
api_key = '4b86073fd285073df5233297bd5f596b'

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

def dl_image(url):
	from PIL import Image
	if not url: return None
	global mark
	mark = util.pause('flickr', mark)
	imname = os.path.split(url)[1]
	print ">>>>>getting flickr img at %s" % url
	try:
		nm, headers = urllib.urlretrieve(url, os.path.join("resources", "images", imname))
	except IOError:
		print "{{ socket timeout for flickr user_images"
		return None
	# cairo can't load jpgs, or I just can't find documentation, wish I hadn't used it...
	im = Image.open(nm)
	os.remove(nm)
	nm = "%s.png" % nm.split(".")[0]
	im.save(nm)
	print ">>>>>> got img file %s ..." % nm
	return nm

def photo_url(link):
	global mark
	mark = util.pause('flickr', mark)
	flickr = flickrapi.FlickrAPI(api_key)
	# expecting something like http://www.flickr.com/photos/ozten/2366650348/
	pid = link.split('/')[5]
	dat = flickr.photos_getSizes(photo_id=pid)
	# return something we can pass directly to Image() constructor
	for sz in dat.sizes[0].size:
		if sz['label'] == 'Small' : return sz['source']
