import urllib, simplejson, util

mark = 0

def social_network(uname):
	global mark
	mark = util.pause('jaiku', mark)
	feed = urllib.urlopen("http://%s.jaiku.com/json" % uname)
	try:
		jobj = simplejson.load(feed)
	except ValueError:
		# user doesnt exist
		return []
	# keys in contacts : "avatar", "first_name", "last_name", "nick", "url"
	return jobj['contacts']

def stuff(uname):
	global mark
	mark = util.pause('jaiku', mark)
	feed = urllib.urlopen("http://%s.jaiku.com/feed/json" % uname)
	try:
		jobj = simplejson.load(feed)
	except ValueError:
		# user doesnt exist
		return []
	# keys in stream : "id", "title", "content", "icon", "url", "created_at", "created_at_relative", "comments", "user"
	return jobj['stream']
	
		
