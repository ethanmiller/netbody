import util, apis.flickr, apis.delic, apis.technorati, apis.jaiku
import random, datetime

entities = {}
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

	def matches(self, other):
		"""the base match checking"""
		return self.id == other.id

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
		# places to store results from api calls
		self.api_res_flickr = []
		self.api_res_delic = []
		self.api_res_tech = []

	def spider(self):
		ret = []
		# currently 5 random samples from each of these...
		limit_to = 5
		# flickr
		if not self.api_res_flickr:
			self.api_res_flickr = apis.flickr.by_tag(self.tag)
			random.shuffle(self.api_res_flickr)
		for i in range(min(limit_to, len(self.api_res_flickr))):
			im = self.api_res_flickr.pop(0)
			ret.append(Image(img_link=im['link'], username=im['author'], author_id=im['author_id'], title=im['title'], tags=im['tags']))
		# del.icio.us
		if not self.api_res_delic:
			self.api_res_delic = apis.delic.by_tag(self.tag)
			random.shuffle(self.api_res_delic)
		for i in range(min(limit_to, len(self.api_res_delic))):
			url = self.api_res_delic.pop(0)
			ret.append(Link(url=url['link'], title=url['title']))
		# technorati
		if not self.api_res_tech:
			self.api_res_tech = apis.technorati.by_tag(self.tag)
			random.shuffle(self.api_res_tech)
		for i in range(min(limit_to, len(self.api_res_tech))):
			blog = self.api_res_tech.pop(0)
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
		# storage for results from api calls:

	class api_res:
		class flickr:
			socnet = []
			images = []
		class delic:
			socnet = []
			links = []
		class jaiku:
			socnet = []
			stuff = []

	def spider(self):
		ret = []
		self.network_count = 0
		self.prep_spider()
		ret = ret + self.spider_flickr()
		ret = ret + self.spider_delic()
		ret = ret + self.spider_jaiku()
		####
		if self.network_count == 0:
			self.spiderable = False # friendless usernames have been leading me into sandpits
		else:
			print "--- a UserName (%s) spiders %s other entities..." % (self.id, len(ret))
		return ret
	
	def matches(self, other):
		"""cross reference names used"""
		# as long as we're careful in collection.spider()
		# self will already part of the collection, while the other is not. So self may have 
		# multiple services already but other should just have one
		if other.names.has_key('flickr_id'):
			if self.names.has_key('flickr_id'): 
				return other.names.get('flickr_id') == self.names.get('flickr_id')
			# for flickr, try matching on url-name, which other may not have (url names are assigned flickr_id if not set)
			if other.names.has_key('flickr_url'):
				for k, v in self.names.iteritems():
					if v == other.names.get('flickr_url'):
						print "^^^ claimed a flickr user via %s = %s" % (k, v)
						self.names.update(other.names)
						return True
			return False # only 1 service per other
		if other.names.has_key('del.icio.us'):
			if self.names.has_key('del.icio.us'): 
				return other.names.get('del.icio.us') == self.names.get('del.icio.us')
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # these aren't formats for del.icio.us names
				if v == other.names.get('del.icio.us'):
					print "^^^ claimed a del.icio.us user via %s = %s" % (k, v)
					self.names.update(other.names)
					return True
			return False
		if other.names.has_key('jaiku'):
			if self.names.has_key('jaiku'):
				return other.names.get('jaiku') == self.names.get('jaiku')
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # these aren't formats for jaiku names
				if v == other.names.get('jaiku'):
					print "^^^ claimed a jaiku user via %s = %s" % (k, v)
					self.names.update(other.names)
					return True
		return False

	def prep_spider(self):
		"""make api calls for services user has, but we have no data"""
		if self.names.has_key('flickr_id'):
			if not self.api_res.flickr.socnet:
				self.api_res.flickr.socnet = apis.flickr.social_network(self.names.get('flickr_id'))
				random.shuffle(self.api_res.flickr.socnet)
			if not self.api_res.flickr.images:
				self.api_res.flickr.images = apis.flickr.user_images(self.names.get('flickr_id'))
				random.shuffle(self.api_res.flickr.images)
		if self.names.has_key('del.icio.us'):
			if not self.api_res.delic.socnet:
				self.api_res.delic.socnet = apis.delic.social_network(self.names.get('del.icio.us'))
				random.shuffle(self.api_res.delic.socnet)
			if not self.api_res.delic.links:
				self.api_res.delic.links = apis.delic.links(self.names.get('del.icio.us'))
				random.shuffle(self.api_res.delic.links)
		if self.names.has_key('jaiku'):
			if not self.api_res.jaiku.socnet:
				self.api_res.jaiku.socnet = apis.jaiku.social_network(self.names.get('jaiku'))
				random.shuffle(self.api_res.jaiku.socnet)
			if not self.api_res.jaiku.stuff:
				self.api_res.jaiku.socnet = apis.jaiku.stuff(self.names.get('jaiku'))
				random.shuffle(self.api_res.jaiku.stuff)

	def spider_flickr(self):
		ret = []
		netct = min(self.limit_to, len(self.api_res.flickr.socnet))
		self.network_count = self.network_count + netct
		for i in range(netct):
			u = self.api_res.flickr.socnet.pop(0)
			dnames = {'flickr_display' : u['author'].split('(')[1][:-1]}
			dnames['flickr_id'] = u['author_id']
			linkname = u['link'].split("/")[4] # when splitting that url, linkname comes after ['http:', '', 'www.flickr.com', 'photos'
			if linkname != u['author_id'] : dnames['flickr_url'] = linkname
			ret.append(UserName(names=dnames))
		# spider photos for user
		for i in range(min(self.limit_to, len(self.api_res.flickr.images))):
			im = self.api_res.flickr.images.pop(0)
			ret.append(Image(img_link=im['link'], username=im['author'], author_id=im['author_id'], title=im['title'], tags=im['tags']))
		return ret

	def spider_delic(self):
		ret = []
		netct = min(self.limit_to, len(self.api_res.delic.socnet))
		self.network_count = self.network_count + 1 # we'll pass del.icio.us users
		for i in range(netct):
			u = self.api_res.delic.socnet.pop(0)
			ret.append(UserName(names={'del.icio.us' : u}))
		for i in range(min(self.limit_to, len(self.api_res.delic.links))):
			l = self.api_res.delic.links.pop(0)
			ret.append(Link(url=l['link'], title=l['title']))
		return ret

	def spider_jaiku(self):
		ret = []
		netct = min(self.limit_to, len(self.api_res.jaiku.socnet))
		self.network_count = self.network_count + netct
		for i in range(netct):
			u = self.api_res.jaiku.socnet.pop(0)
			ret.append(UserName(names={'jaiku' : u['nick']}))
		for i in range(min(self.limit_to, len(self.api_res.jaiku.stuff))):
			s = self.api_res.jaiku.stuff.pop(0)
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
		self.api_res_delic = []

	def spider(self):
		ret = []
		limit_to = 5
		if not self.api_res_delic:
			self.api_res_delic = apis.delic.url_data(self.url)
			random.shuffle(self.api_res_delic)
		for i in range(min(limit_to, len(self.api_res_delic))):
			dat = self.api_res_delic.pop(0)
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
		if len(entities.keys()) > 0 : raise RuntimeError, "spider without argument only to initialize"
		entity = Tag(tag='identity')
		entity.index = 0
		entities[str(entity.__class__)] = [entity]
	else:
		entity = seed
	entity.active = True
	print '\n\n__main spider() call on entity id=%s [%s]__ %s' % (entity.id, entity.__class__, datetime.datetime.today().strftime("%a %I:%M%p"))
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
	ekey = str(entity.__class__)
	if entities.has_key(ekey):
		for e in entities[ekey]:
			if e.matches(entity): return False, e
		entity.index = len(entities[ekey])
		entities[ekey].append(entity)
		return True, entity
	else:
		entities[ekey] = [entity]
		return True, entity

if __name__ == '__main__':
	util.log('INIT')
	spider()
	for e in entities:
		print dir(e)
