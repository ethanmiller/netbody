import util
import random, simplejson, urllib, re, os

class Collector:
	def __init__(self):
		self.jpgstr = re.compile("http[^'\"]*\.jpg")
	
	def data(self):
		images = filter(lambda x: not x.startswith('.'), os.listdir('resources/images'))
		# TODO do this intelligently
		return ['resources/images/%s' % random.choice(images) for x in range(random.randint(0, 6))]

	def proc_json(self):
		feed = urllib.urlopen(util.CONST.FEED_URL)
		jobj = simplejson.loads(feed.read())
		for entry in jobj['value']['items']:
			if entry['title'] == util.CONST.TITLE_FLICKR_RECENT:
				words, images = self.proc_flickr(entry)
				# dl images
				for i in images:
					self.store_img(i)
			elif entry['title'] == util.CONST.TITLE_NEWS_TOP:
				words, images = self.proc_news_top(entry)
				# dl images
				for i in images:
					self.store_img(i)
			elif entry['title'] == util.CONST.TITLE_NEWS_PHOTOS:
				words, images = self.proc_news_photos(entry)
				# dl images
				for i in images:
					self.store_img(i)

	def store_img(self, url):
		fname = 'resources/%s' % url.split('/')[-1]
		urllib.urlretrieve(url, fname)
		print 'got %s' % fname

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
	
		
