import subprocess, feedparser, urlparse, time, os, util

mark = 0

def by_tag(t):
	global mark
	mark = util.pause('YouTube', mark)
	fobj = feedparser.parse(u"http://www.youtube.com/rss/tag/%s.rss" % unicode(t))
	return fobj['entries']

def vids(uname):
	global mark
	mark = util.pause('YouTube', mark)
	fobj = feedparser.parse(u"http://www.youtube.com/rss/user/%s/videos.rss" % uname)
	return fobj['entries']

def get_vid(id, url):
	return subprocess.Popen("python apis/youtube-dl.py -q -o resources/videos/%s.flv %s" % (id, url), shell=True)

def split_vid(id):
	# first 15 seconds of video
	return subprocess.Popen("cd resources/videos/%s;mplayer -really-quiet -endpos 15 -vo png -nosound ../%s.flv" % (id, id), shell=True)

def extract_audio(id):
	return subprocess.Popen("cd resources/videos/%s;mplayer -really-quiet -dumpaudio ../%s.flv -dumpfile audio.mp3" % (id, id), shell=True)

# keys in fobj['entries'] = ['media_category', 'summary_detail', 'media_credit', 
# 'updated_parsed', 'links', 'title', 'media_player', 'author', 'updated', 
# 'media_thumbnail', 'summary', 'guidislink', 'title_detail', 'link', 'author_detail', 'id', 'enclosures']
# use 'media_category' for tags
# 'media_credit' for username
# 'link' for link
