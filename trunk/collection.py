import util, apis.flickr, apis.delic, apis.technorati
import random

entities = []
seed = None

class Entity:
	def __init__(self, *args, **kwargs):
		for k,v in kwargs.iteritems():
			setattr(self, k, v)
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
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, **kwargs)
		self.id = kwargs['img_link']

class Tag(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, **kwargs)
		self.id = kwargs['tag']

	def spider(self):
		ret = []
		for im in apis.flickr.by_tag(self.tag):
			ret.append(Image(img_link=im['link'], username=im['author'], title=im['title']))
		for url in apis.delic.by_tag(self.tag):
			ret.append(Link(url=url['link'], title=url['title']))
		for blog in apis.technorati.by_tag(self.tag):
			ret.append(BlogPost(blog_link=blog['link'], title=blog['title']))
		print "tag spiders %s others", len(ret)
		return ret
		

class BlogPost(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, **kwargs)
		self.id = kwargs['blog_link']

class UserName(Entity):
	def __init__(self):
		pass

class Link(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, **kwargs)
		self.id = kwargs['url']

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
	network = entity.spider()
	rchoice = random.randrange(len(network))
	for i, e in enumerate(entity.spider()):
		e = get_or_add(e)
		e.active = True
		if rchoice == i : 
			seed = e # choose a seed for next spider
			print "seed id = %s" % e.id

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
