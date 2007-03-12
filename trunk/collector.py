import util
import random, simplejson, urllib, re, os, time, socket
from pysqlite2 import dbapi2 as sqlite

class Collector:
	def __init__(self):
		self.jpgstr = re.compile("http[^'\"]*\.jpg")
		self.initdb()
		self.time = self.lasttime = time.time()

	def initdb(self):
		conn = sqlite.connect(util.CONST.DB_LOC, isolation_level=None)
		cur = conn.cursor()
		# find out if this db has already been setup
		cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tablenames = [name for name in cur]
		if tablenames:
			# reset used flag
			cur.execute("UPDATE images SET used=0;")
		else:
			# define our three tables...
			cur.executescript("""
			CREATE TABLE images (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				path TEXT,
				date TEXT DEFAULT CURRENT_TIMESTAMP,
				used INTEGER
			);
			CREATE TABLE words (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				word TEXT
			);
			CREATE TABLE wordimage (
				wordid INTEGER NOT NULL,
				imageid INTEGER NOT NULL
			);
			""")
		cur.close()
		conn.close()
	
	def data(self):
		retcount = random.randint(*util.CONST.IMG_PER_FRAME_RANGE)
		if retcount == 0:
			return []
		#return a few fresh images
		conn = sqlite.connect(util.CONST.DB_LOC, isolation_level=None)
		conn.row_factory = sqlite.Row
		cur = conn.cursor()
		cur.execute("SELECT * FROM images WHERE used=0 ORDER BY date ASC LIMIT %s;" % retcount)
		# data structure for an image + associated words.. possibly more than one...
		# [{'imgid' : n, 'img' : '/path/to/image', 'words' : ['a', 'b', 'c']}, {..}, ...]
		imgs = [{'imgid' : row['id'], 'img' : row['path'], 'words' : []} for row in cur]
		for i in imgs:
			cur.execute("SELECT * FROM wordimage, words WHERE words.id=wordimage.wordid AND wordimage.imageid=%s;" % i['imgid'])
			for row in cur:
				i['words'].append(row['word'])
		if imgs:
			# mark them used
			cur.execute("UPDATE images SET used=1 WHERE images.id IN (%s);" % ','.join([str(x['imgid']) for x in imgs]))
		else:
			# we must be out of fresh images... if enough time has passed - get more
			self.time = time.time()
			if self.time - self.lasttime > util.CONST.COLLECTION_PAUSE:
				self.proc_json()
				self.lasttime = self.time
		cur.close()
		conn.close()
		return imgs

	def proc_json(self):
		socket.setdefaulttimeout(util.CONST.FEED_TIMEOUT)
		try:
			feed = urllib.urlopen(util.CONST.FEED_URL)
			jobj = simplejson.loads(feed.read())
			socket.setdefaulttimeout(util.CONST.IMG_TIMEOUT)
			for entry in jobj['value']['items']:
				if entry['title'] == util.CONST.TITLE_FLICKR_RECENT:
					self.storedata(*self.proc_flickr(entry))
				elif entry['title'] == util.CONST.TITLE_NEWS_TOP:
					self.storedata(*self.proc_news_top(entry))
				elif entry['title'] == util.CONST.TITLE_NEWS_PHOTOS:
					self.storedata(*self.proc_news_photos(entry))
		except IOError:
			print "-- feed took longer than %s seconds --" % util.CONST.FEED_TIMEOUT
		#self.print_tables('images')
		#self.print_tables('wordimage')

	def storedata(self, words, imgs):
		conn = sqlite.connect(util.CONST.DB_LOC, isolation_level=None)
		conn.row_factory = sqlite.Row
		cur = conn.cursor()

		# check if any of these words have been added already, insert new words
		words_by_id = {}
		for w in words:
			cur.execute("SELECT * FROM words WHERE word='%s';" % w.lower())
			row = cur.fetchone()
			if row:
				words_by_id[row['id']] = w
				continue
			cur.execute("INSERT INTO words (word) VALUES ('%s');" % w.lower())
			# get generated ID for that word
			print "adding word: %s" % w
			cur.execute("SELECT * FROM words WHERE word='%s';" % w.lower())
			row = cur.fetchone()
			words_by_id[row['id']] = w

		# now images... add if that image name is not already in there....
		# note: if the same filename pops up, this will just keep the old one and forget the new one...
		for i in imgs:
			fname = 'resources/images/%s' % i.split('/')[-1].lower()
			cur.execute("SELECT * FROM images WHERE path='%s';" % fname)
			row = cur.fetchone()
			if row:
				print "{{{ALREADY}} got %s --------------------" % fname
				# already got this image
				continue
			# actually get the image...
			print 'downloading %s' % i
			try:
				stream = urllib.urlretrieve(i, fname)
				print "got it!"
				cur.execute("INSERT INTO images (path, used) VALUES ('%s', 0);" % fname)
				# now create many-to-many record
				cur.execute("SELECT * FROM images WHERE path='%s';" % fname)
				row = cur.fetchone()
				sql = ''
				for wid, w in words_by_id.iteritems():
					sql += "INSERT INTO wordimage (wordid, imageid) VALUES (%s, %s);" % (wid, row['id'])
				cur.executescript(sql)
			except IOError:
				print "failed..."
		#finished......
		cur.close()
		conn.close()
			
	def print_tables(self, table):
		# debugging utility...
		conn = sqlite.connect(util.CONST.DB_LOC, isolation_level=None)
		cur = conn.cursor()
		cur.execute("SELECT * FROM %s;" % table)
		for desc in cur.description:
			print desc[0].ljust(20) ,
		print # newline
		print '-' * 80
		fieldIndices = range(len(cur.description))
		for row in cur:
			for fieldIndex in fieldIndices:
				fieldValue = unicode(row[fieldIndex])
				print fieldValue.ljust(20) ,
			print # newline

	def proc_news_photos(self, entry):
		w = entry['y:content_analysis'].split(' ')
		i = [entry['media:content']['url'].split('?')[0]] # getting rid of the query string gets us a larger image
		return w, i

	def proc_news_top(self, entry):
		w = entry['y:content_analysis'].split(' ')
		i = []
		for img in entry['flick']:
			i.append(img['y:flickr']['img'])
		return w, i

	def proc_flickr(self, entry):
		if type(entry['category']) == list:
			w = [x['term'] for x in entry['category']]
		else:
			w = [entry['category']['term']]
		m = self.jpgstr.search(entry['content']['content'])
		i = [m.group()]
		return w, i

if __name__ == '__main__':
	col = Collector()
	col.proc_json()
	
		
