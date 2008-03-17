import util, apis.flickr, apis.delic, apis.technorati
entities = []

class Entity:
	def __init__(self, *args, **kwargs):
		for k,v in kwargs.iteritems():
			setattr(self, k, v)
		self.active = False

	def spider(self):
		"""spider is always overidden"""
		return []

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

def spider(entity=None):
	global entities
	if not entity: 
		if len(entities) > 0 : raise RuntimeError, "spider without argument only to initialize"
		entity = Tag(tag='identity')
		entity.index = 0
		entities.append(entity)
	for e in entity.spider():
		e = get_or_add(e)
		e.active = True

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
