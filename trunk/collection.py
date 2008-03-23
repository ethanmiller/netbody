import util, apis.flickr, apis.delic, apis.technorati
import random

entities = []
seed = None

class Entity:
	""" Base class for all entities in netbody visualization """
	def __init__(self, kwarg_keys, **kwargs):
		chkwargs = kwarg_keys[:]
		for k,v in kwargs.iteritems():
			if k not in chkwargs: raise TypeError, "Unexpected arg :: %s" % k
			indxof = chkwargs.index(k)
			del(chkwargs[indxof])
			setattr(self, k, v)
		if chkwargs: raise TypeError, "Missing arg(s) :: %s" % chkwargs
		self.active = False
		self.tmp_draw_ct = 50 # time it will take to render this entity

	def spider(self):
		"""spider is always overidden"""
		raise RuntimeError, "Must override base Entity spider()"

	def draw(self):
		if self.active:
			if self.tmp_draw_ct == 0:
				# done drawing
				self.active = False
				self.tmp_draw_ct = 50
			else:
				self.tmp_draw_ct = self.tmp_draw_ct - 1

class Image(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['img_link', 'username', 'title', 'tags'], **kwargs)
		self.id = kwargs['img_link']
		# username attr came in the form "nobody@flickr.com (username)"
		self.username = self.username.split('(')[1][:-1]
		# taglist is space separated
		self.tags = self.tags.split(' ')

	def spider(self):
		''' When Image inits, we already have a tag list and the username - create obj based on that...'''
		ret = []
		for t in self.tags:
			ret.append(Tag(tag=t))
		ret.append(UserName(username=self.username))
		print "--- an Image (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

class Tag(Entity):
	""" Tag Entity just expects a 'tag' argument in constructor """
	def __init__(self, **kwargs):
		Entity.__init__(self, ['tag'], **kwargs)
		self.id = kwargs['tag']

	def spider(self):
		ret = []
		for im in apis.flickr.by_tag(self.tag):
			ret.append(Image(img_link=im['link'], username=im['author'], title=im['title'], tags=im['tags']))
		#for url in apis.delic.by_tag(self.tag):
			#ret.append(Link(url=url['link'], title=url['title']))
		#for blog in apis.technorati.by_tag(self.tag):
			#ret.append(BlogPost(blog_link=blog['link'], title=blog['title']))
		print "--- a Tag (%s) spiders %s other entities..." % (self.tag, len(ret))
		return ret
		

class BlogPost(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['blog_link', 'title'], **kwargs)
		self.id = kwargs['blog_link']

class UserName(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['username'], **kwargs)
		self.id = kwargs['username']

class Link(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['url', 'title'], **kwargs)
		self.id = kwargs['url']

	def spider(self):
		ret = []
		for dat in apis.delic.url_data(self.url):
			for tdict in dat['tags']:
				for t in tdict['term'].split(' '):
					ret.append(Tag(tag=t))
			ret.append(UserName(username=dat['author']))
		return ret

def spider():
	global entities, seed
	if not seed: 
		if len(entities) > 0 : raise RuntimeError, "spider without argument only to initialize"
		entity = Tag(tag='identity')
		entity.index = 0
		entities.append(entity)
	else:
		entity = seed
	entity.active = True
	print '__main spider() call on entity id=%s [%s]__' % (entity.id, entity.__class__)
	network = entity.spider() 
	rchoice = 4 #random.randrange(len(network))
	for i, e in enumerate(network):
		e = get_or_add(e)
		e.active = True
		if rchoice == i : 
			seed = e # choose a seed for next spider
			print "seed id = %s [%s]" % (e.id, e.__class__)

def get_or_add(entity):
	"""if the entity is in the collection already, return the collected one. Otherwise add it to collection"""
	for e in entities:
		if e.id == entity.id and e.__class__ == entity.__class__: return e
	entity.index = len(entities)
	entities.append(entity)
	return entity

if __name__ == '__main__':
	util.log('INIT')
	spider()
	for e in entities:
		print dir(e)