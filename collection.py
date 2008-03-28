import util, apis.flickr, apis.delic, apis.technorati, apis.jaiku
import random

entities = []
seed = None
pnetwork = None

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
		self.spiderable = True

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
		Entity.__init__(self, ['img_link', 'author_id', 'username', 'title', 'tags'], **kwargs)
		self.id = kwargs['img_link']
		# username attr came in the form "nobody@flickr.com (username)"
		self.username = self.username.split('(')[1][:-1]
		# taglist is space separated, unless it's a list alerady
		if type(self.tags) != list : self.tags = self.tags.split(' ')

	def spider(self):
		''' When Image inits, we already have a tag list and the username - create obj based on that...'''
		ret = []
		# could have gobs of tags..
		for t in random.sample(self.tags, min(len(self.tags), 10)):
			t = t.strip()
			if len(t) > 1 : ret.append(Tag(tag=t))
		dnames = {'flickr_display' : self.username, 'flickr_id' : self.author_id}
		urlname = self.img_link.split("/")[4]
		if urlname != self.author_id : dnames['flickr_url'] = urlname
		ret.append(UserName(names=dnames))
		print "--- an Image (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

class Tag(Entity):
	""" Tag Entity just expects a 'tag' argument in constructor """
	def __init__(self, **kwargs):
		Entity.__init__(self, ['tag'], **kwargs)
		self.id = kwargs['tag']

	def spider(self):
		ret = []
		# currently 5 random samples from each of these...
		limit_to = 5
		fk = apis.flickr.by_tag(self.tag)
		for im in random.sample(fk, min(len(fk), limit_to)):
			ret.append(Image(img_link=im['link'], username=im['author'], author_id=im['author_id'], title=im['title'], tags=im['tags']))
		dl = apis.delic.by_tag(self.tag)
		for url in random.sample(dl, min(len(dl), limit_to)):
			ret.append(Link(url=url['link'], title=url['title']))
		tc = apis.technorati.by_tag(self.tag)
		for blog in random.sample(tc, min(len(tc), limit_to)):
			ret.append(BlogPost(blog_link=blog['link'], title=blog['title'], summary=blog.get('summary', '')))
		print "--- a Tag (%s) spiders %s other entities..." % (self.tag, len(ret))
		return ret
		

class BlogPost(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['blog_link', 'title', 'summary'], **kwargs)
		self.id = kwargs['blog_link']

	def spider(self):
		import apis.yahoo
		ret = []
		# summary gave us a little text description of the blog post...
		# yahoo term extration gets 'keywords' out of that...
		for term in apis.yahoo.termExtraction(self.summary):
			for t in term.split(' '):
				t = t.strip()
				if len(t) > 1 and t not in util.CONST.NOISE_WORDS: ret.append(Tag(tag=t))
		print "--- a BlogPost (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

class UserName(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['names'], **kwargs)
		self.id = reduce(lambda n, n2 : n + n2, self.names.values()) # just has to be a unique id
		self.limit_to = 5

	def spider(self):
		ret = []
		self.network_count = 0
		ret = ret + self.spider_flickr()
		ret = ret + self.spider_delic()
		ret = ret + self.spider_jaiku()
		# TODO more possibilities in this spider... jaiku?
		####
		if self.network_count == 0:
			self.spiderable = False # friendless usernames have been leading me into sandpits
		else:
			print "--- a UserName (%s) spiders %s other entities..." % (self.id, len(ret))
		return ret

	def spider_flickr(self):
		ret = []
		if not self.names.has_key('flickr_id'):
			for k, v in self.names.iteritems():
				id = apis.flickr.check_for_user(v) # make an attempt to find on flickr
				if id:
					self.names['flickr_id'] = id
					self.names['flickr_url'] = v
					break
		if self.names.has_key('flickr_id'):
			# spider flickr network
			fnet = apis.flickr.social_network(self.names.get('flickr_id'))
			self.network_count = self.network_count + len(fnet)
			for u in random.sample(fnet, min(len(fnet), self.limit_to)):
				dnames = {'flickr_display' : u['author'].split('(')[1][:-1]}
				dnames['flickr_id'] = u['author_id']
				linkname = u['link'].split("/")[4] # when splitting that url, linkname comes after ['http:', '', 'www.flickr.com', 'photos'
				if linkname != u['author_id'] : dnames['flickr_url'] = linkname
				ret.append(UserName(names=dnames))
			# spider photos for user
			fph = apis.flickr.user_images(self.names.get('flickr_id'))
			for im in random.sample(fph, min(len(fph), self.limit_to)):
				ret.append(Image(img_link=im['link'], username=im['author'], author_id=im['author_id'], title=im['title'], tags=im['tags']))
		return ret

	def spider_delic(self):
		ret = []
		dnet = []
		if not self.names.has_key('del.icio.us'):
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # these aren't formats for del.icio.us names
				dnet = apis.delic.social_network(v)
				if len(dnet) > 0:
					# we found a del.icio.us user
					print "^^^ found a del.icio.us user with %s = %s" % (k, v)
					self.names['del.icio.us'] = v
					break
			if not dnet : return []
		else:
			dnet = apis.delic.social_network(self.names.get('del.icio.us'))
		self.network_count = self.network_count + len(dnet)
		for u in random.sample(dnet, min(len(dnet), self.limit_to)):
			# just returns a list of usernames
			ret.append(UserName(names={'del.icio.us' : u}))
		dln = apis.delic.links(self.names.get('del.icio.us'))
		for l in random.sample(dln, min(len(dln), self.limit_to)):
			ret.append(Link(url=l['link'], title=l['title']))
		return ret

	def spider_jaiku(self):
		ret = []
		if not self.names.has_key('jaiku'):
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # these aren't formats for del.icio.us names
				jnet = apis.jaiku.social_network(v)
				if len(jnet) > 0:
					print "^^^ found a jaiku user with %s = %s" % (k, v)
					self.names['jaiku'] = v
					break
			if not jnet : return []
		else:
			jnet = apis.jaiku.social_network(self.names.get('jaiku'))
		self.network_count = self.network_count + len(jnet)
		for u in random.sample(jnet, min(len(jnet), self.limit_to)):
			ret.append(UserName(names={'jaiku' : u['nick']}))
		jstuff = apis.jaiku.stuff(self.names.get('jaiku'))
		for s in random.sample(jstuff, min(len(jstuff), self.limit_to)):
			# different kind of objects for different stuff
			if s['url'].find("flickr.com") >= 0:
				print "got Image from jaiku feed"
				ret.append(Image(**apis.flickr.photo_data(s['url'])))
			# add twitter here
		return ret
			

class Link(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['url', 'title'], **kwargs)
		self.id = kwargs['url']

	def spider(self):
		ret = []
		limit_to = 5
		udat = apis.delic.url_data(self.url)
		for dat in random.sample(udat, min(len(udat), limit_to)):
			tags_added = 0 
			for tdict in dat['tags']:
				for t in tdict['term'].split(' '):
					if tags_added > 3 : break # 3 tags per record ..
					t = t.strip()
					if len(t) > 1 : 
						ret.append(Tag(tag=t))
						tags_added = tags_added + 1
			ret.append(UserName(names={'del.icio.us' : dat['author']}))
		print "--- a Link (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

def spider():
	global entities, seed, pnetwork
	if not seed: 
		if len(entities) > 0 : raise RuntimeError, "spider without argument only to initialize"
		entity = Tag(tag='identity')
		entity.index = 0
		entities.append(entity)
	else:
		entity = seed
	entity.active = True
	print '\n\n__main spider() call on entity id=%s [%s]__' % (entity.id, entity.__class__)
	network = entity.spider() 
	ncount = len(network)
	if ncount == 0 or not entity.spiderable:
		print "~~found 0 other entities, or nonspiderable entity. Reverting to last set"
		network = pnetwork # reuse the last set and hope we get unstuck
		ncount = len(network)
	else:
		pnetwork = network # save this network in case we need to come back to it
	rchoice = random.randrange(len(network))
	addcount = 0
	for i, e in enumerate(network):
		added, e = get_or_add(e)
		if added: addcount += 1
		e.active = True
		if rchoice == i : 
			seed = e # choose a seed for next spider
			print "seed id = %s [%s]" % (e.id, e.__class__)
	print "++ %s entities, and %s of those were new ++" % (ncount, addcount)

def get_or_add(entity):
	"""if the entity is in the collection already, return the collected one. Otherwise add it to collection
	returns boolean added, and obj"""
	for e in entities:
		if e.id == entity.id and e.__class__ == entity.__class__: return False, e
	entity.index = len(entities)
	entities.append(entity)
	return True, entity

if __name__ == '__main__':
	util.log('INIT')
	spider()
	for e in entities:
		print dir(e)
