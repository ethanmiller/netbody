import util, apis.flickr, apis.delic, apis.technorati, apis.youtube
import random, datetime, urllib2, socket, os
from vec2d import vec2d

socket.setdefaulttimeout(15)

entities = {}
seed = None
pnetwork = None
posi = None

class Positioner:
	def __init__(self):
		""" This class keeps track of entity positions and dimensions 
			It will determine position in relation to other positions and dimensions 
			But entities have to update this class with their dimensions
		"""
		self.entities = {} # containing : {'class_name' : {'colx' : 0, 'entity_pos' : [(x,y,w,h), (x,y,w,h), ...]}, ... }
		# the x position of each entity is relative to the colx so that I can push over the whole column
		self.total_width = 0

	def add_node(self, type):
		if not self.entities.has_key(type):
			nx = self.total_width + util.CONST.GRID_SPACE
			xywh = (0, util.CONST.GRID_SPACE, util.CONST.ENTITY_DEFAULT_SIZE, util.CONST.ENTITY_DEFAULT_SIZE)
			self.entities[type] = {'colx' :	nx, 'entity_pos' : [xywh]}
			self.total_width = self.total_width + util.CONST.GRID_SPACE
		else:
			# last entity_pos gives ypos
			ny = self.entities[type]['entity_pos'][-1][1] + util.CONST.GRID_SPACE
			nx = self.entities[type]['entity_pos'][-1][0] # make the xpos same as previous pos
			if ny >= util.CONST.WIN_HEIGHT:
				# we have to bump the other columns to the right
				for e in self.entities.values():
					if e['colx'] > self.entities[type]['colx']: e['colx'] = e['colx'] + util.CONST.GRID_SPACE
				self.entities[type]['colx'] = self.entities[type]['colx'] + util.CONST.GRID_SPACE
				nx = nx + util.CONST.GRID_SPACE
				ny = util.CONST.GRID_SPACE
			self.entities[type]['entity_pos'].append((nx, ny, util.CONST.ENTITY_DEFAULT_SIZE, util.CONST.ENTITY_DEFAULT_SIZE))

	def update_size(self, type, index, w, h):
		xywh = self.entities[type]['entity_pos'][index]
		self.entities[type]['entity_pos'][index] = (xywh[0], xywh[1], w, h)

	def get_pos(self, type, index):
		"""each entity will always get position from here"""
		cx = self.entities[type]['colx']
		return (cx + self.entities[type]['entity_pos'][index][0], self.entities[type]['entity_pos'][index][1])

class Curve:
	""" A curve owned by an entity to connect it to another entity """
	def __init__(self, otype, oindx):
		self.end_type = otype
		self.end_indx = oindx
		self.control_pts = []
		self.control_xoff = (random.randint(util.CONST.CURVE_X_VAR_MIN, util.CONST.CURVE_X_VAR_MAX), random.randint(util.CONST.CURVE_X_VAR_MIN, util.CONST.CURVE_X_VAR_MAX))
		self.segments = random.randint(util.CONST.CURVE_SEG_MIN, util.CONST.CURVE_SEG_MAX)
		self.curve_pts = []
		self.curve_indx = 0
		self.last_oxy = (0, 0)

	def matches(self, t, i):
		return self.end_type == t and self.end_indx == i

	def calc_ctrl_pts(self, x, y):
		ox, oy = posi.get_pos(self.end_type, self.end_indx)
		# randomize the horizontal change, leave the vertical aligned
		x1 = max(x, ox) + self.control_xoff[0]
		y1 = y
		x2 = max(x, ox) + self.control_xoff[1]
		y2 = oy
		self.control_pts = [vec2d(x, y), vec2d(x1, y1), vec2d(x2, y2), vec2d(ox, oy)]

	def set_ctrl_pts(self, x, y, that_xy_changed):
		oxy = posi.get_pos(self.end_type, self.end_indx)
		this_xy_changed = oxy != self.last_oxy
		self.last_oxy = oxy
		if not self.control_pts or that_xy_changed or this_xy_changed:
			self.calc_ctrl_pts(x, y)

	def set_curve_pts(self, that_xy_changed):
		if not self.control_pts: raise RuntimeError, "Have to set control points before calculating curve points"
		oxy = posi.get_pos(self.end_type, self.end_indx)
		this_xy_changed = oxy != self.last_oxy
		self.last_oxy = oxy
		if not self.curve_pts or that_xy_changed or this_xy_changed:
			self.curve_pts = util.calculate_bezier(self.control_pts, self.segments)

	def draw(self, ctx, isactive):
		# draw out as much of the curve as we have at this point
		ret_curve_done = True
		if isactive:
			# draw segment by segment
			if self.curve_indx < len(self.curve_pts): 
				self.curve_indx = self.curve_indx + 1
				ret_curve_done = False
			ctx.move_to(self.curve_pts[0][0], self.curve_pts[0][1])
			for i, p in enumerate(self.curve_pts[:self.curve_indx]):
				if i == 0 : continue
				ctx.line_to(p[0], p[1])
		else:
			# just draw the curve
			ctx.move_to(self.control_pts[0][0], self.control_pts[0][1])
			ctx.curve_to(self.control_pts[1][0], self.control_pts[1][1], 
						self.control_pts[2][0], self.control_pts[2][1],
						self.control_pts[3][0], self.control_pts[3][1])
		ctx.stroke()
		return ret_curve_done

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
		self.last_xy = (0, 0)
		self.active = False
		self.is_seed = False
		self.width = util.CONST.ENTITY_DEFAULT_SIZE
		self.ext_width = util.CONST.ENTITY_DEFAULT_SIZE
		self.height = util.CONST.ENTITY_DEFAULT_SIZE
		self.ext_height = util.CONST.ENTITY_DEFAULT_SIZE
		self.spiderable = True
		self.curves = []

	def has_curve(self, type, indx):
		for c in self.curves:
			if c.matches(type, indx): return True
		return False
	
	def add_connection(self, type, indx):
		if not self.has_curve(type, indx):
			self.curves.append(Curve(type, indx))

	def del_connection(self, type, indx):
		for i, c in enumerate(self.curves):
			if c.matches(type, indx): del(self.curves[i]); return

	def approve(self):
		"""any expensive opperations go here instead of __init__"""
		pass

	def spider(self):
		"""spider is always overidden"""
		raise RuntimeError, "Must override base Entity spider()"

	def matches(self, other):
		"""the base match checking"""
		return self.id == other.id


	def draw(self, ctx):
		# have we moved?
		xy = posi.get_pos(str(self.__class__), self.index)
		has_changed = xy != self.last_xy
		self.last_xy = xy
		curves_done = True
		for curve in self.curves:
			curve.set_ctrl_pts(xy[0], xy[0], has_changed)
			curve.set_curve_pts(has_changed)
			if not curve.draw(ctx, self.active): curves_done = False
		if curves_done:
			self.active = False
			self.is_seed = False		
					
		if self.is_seed : ctx.set_source_rgb(1.0, 0.2, 0.2)
		else : ctx.set_source_rgb(0.2, 0.2, 0.2)
		ctx.rectangle(xy[0], xy[1], self.width, self.height)
		#ctx.close_path()
		ctx.fill()
		

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
		self.api_res_yt = []

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
		# youtube
		if not self.api_res_yt:
			self.api_res_yt = apis.youtube.by_tag(self.tag)
			random.shuffle(self.api_res_yt)
		# better get just 2 at a time
		for i in range(min(2, len(self.api_res_yt))):
			yt = self.api_res_yt.pop(0)
			ret.append(Video(url=yt['link'], title=yt['title'], username=yt['media_credit'], tags=yt['media_category']))
		print "--- a Tag (%s) spiders %s other entities..." % (self.tag, len(ret))
		return ret

class BlogPost(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['blog_link', 'title', 'summary'], **kwargs)
		self.id = kwargs['blog_link']
		self.status = 200

	def approve(self):
		try:
			urllib2.urlopen(self.blog_link)
		except urllib2.HTTPError, e:
			print "0000 problem with url %s 00000 returned code %s" % (self.blog_link, e.code)
			self.status = e.code
		except urllib2.URLError:
			print "0000 problem with url %s 00000 ------- calling it 404" % self.blog_link
			self.status = 400

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
		class yt:
			vids = []

	def spider(self):
		ret = []
		self.network_count = 0
		self.branch_out()
		self.prep_spider()
		ret = ret + self.spider_flickr()
		ret = ret + self.spider_delic()
		ret = ret + self.spider_yt()
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
		if other.names.has_key('youtube'):
			if self.names.has_key('youtube'):
				return other.names.get('youtube') == self.names.get('youtube')
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # these aren't formats for yt names
				if v == other.names.get('youtube'):
					print "^^^ claimed a youtube user via %s = %s" % (k, v)
					self.names.update(other.names)
					return True
			return False
	
	def branch_out(self):
		if not self.names.has_key('flickr_id'):
			# check for a flickr user with one of my names
			for k, v in self.names.iteritems():
				id = apis.flickr.check_for_user(v)
				if id:
					self.names['flickr_id'] = id
					self.names['flickr_url'] = v
					break
		if not self.names.has_key('del.icio.us'):
			# check for del.icio.us user
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # won't happen
				self.api_res.delic.links = apis.delic.links(v)
				if self.api_res.delic.links:
					print "^^^ discovered a del.icio.us user with %s = %s" % (k, v)
					self.names["del.icio.us"] = v
					break
		if not self.names.has_key('youtube'):
			# check for youtube user
			for k, v in self.names.iteritems():
				if k in ['flickr_id', 'flickr_display'] : continue # won't happen
				self.api_res.yt.vids = apis.youtube.vids(v)
				if self.api_res.yt.vids:
					print "^^^ discovered a youtube user with %s = %s" % (k, v)
					self.names["youtube"] = v
					break

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
		if self.names.has_key('youtube'):
			if not self.api_res.yt.vids:
				self.api_res.yt.vids = apis.youtube.vids(self.names.get('youtube'))
				random.shuffle(self.api_res.yt.vids)

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

	def spider_yt(self):
		ret = []
		# just get 2 vids
		for i in range(min(2, len(self.api_res.yt.vids))):
			yt = self.api_res.yt.vids.pop(0)
			ret.append(Video(url=yt['link'], title=yt['title'], username=yt['media_credit'], tags=yt['media_category']))
		return ret

class Link(Entity):
	def __init__(self, **kwargs):
		Entity.__init__(self, ['url', 'title'], **kwargs)
		self.id = kwargs['url']
		self.api_res_delic = []
		self.status = 200

	def approve(self):
		try:
			urllib2.urlopen(self.url)
		except urllib2.HTTPError, e:
			print "0000 problem with url %s 00000 returned code %s" % (self.url, e.code)
			self.status = e.code
		except urllib2.URLError:
			print "0000 problem with url %s 00000 ------- calling it 404" % self.url
			self.status = 400

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

class Video(Entity):
	def __init__(self, **kwargs):
		import urlparse
		Entity.__init__(self, ['url', 'title', 'username', 'tags'], **kwargs)
		q = urlparse.urlparse(self.url)[4]
		self.id = q.split("=")[1]
		self.status = 200
		if type(self.tags) != list : self.tags = self.tags.split(' ')
		self.proc_stage = 0
		self.dl = None
		self.splitvid = None
		self.splitaud = None

	def approve(self):
		self.proc_files()
	
	def proc_files(self):
		if self.proc_stage == 0:
			# get the flv file
			if self.dl == None:
				self.dl = apis.youtube.get_vid(self.id, self.url)
				return # initiate download
			if self.dl.poll() == None: 
				return # still downloading
			if self.dl.poll() == 0:
				print "YT got file %s" % self.title
				self.proc_stage = 1
			else:
				print "YT download on %s got ERR" % self.title
				self.status = 404
				self.proc_stage = -1 # to end this processing now...
		if self.proc_stage == 1:
			if self.splitvid == None:
				os.mkdir("resources/videos/%s" % self.id)
				self.splitvid = apis.youtube.split_vid(self.id) # start splitting video into individual frames
				return
			if self.splitvid.poll() == None:
				return # still splitting
			if self.splitvid.poll() == 0:
				print "YT split vid %s finished" % self.title
				self.proc_stage = 2
			else:
				print "YT split vid %s got ERR" % self.title
				self.proc_stage = -1
		if self.proc_stage == 2:
			if self.splitaud == None:
				self.splitaud = apis.youtube.extract_audio(self.id) # create an audio file from movie
				return
			if self.splitaud.poll() == None:
				return # still extracting
			if self.splitaud.poll() == 0:
				print "YT extract audio %s finished" % self.title
				self.proc_stage = 3
			else:
				print "YT extract audio %s got ERR" % self.title
				self.proc_stage = -1

	def spider(self):
		"""already have user, and tags"""
		ret = []
		for t in random.sample(self.tags, min(len(self.tags), 8)):
			t = t.strip()
			if len(t) > 1 : ret.append(Tag(tag=t))
		ret.append(UserName(names={'youtube' : self.username}))
		print "--- a YouTube Vid (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

	def draw(self, ctx):
		self.proc_files()
		Entity.draw(self, ctx)

def spider():
	global entities, seed, pnetwork, posi
	if not posi:
		posi = Positioner()
	if not seed: 
		if len(entities.keys()) > 0 : raise RuntimeError, "spider without argument only to initialize"
		entity = Tag(tag='identity')
		entity.is_seed = True
		entity.index = 0
		entities[str(entity.__class__)] = [entity]
		posi.add_node(str(entity.__class__))
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
		# this flag lets entity know to animate
		e.active = True
		# make sure spidering entity has all the connections
		entity.add_connection(str(e.__class__), e.index)
		e.del_connection(str(entity.__class__), entity.index)
		if rchoice == i : 
			seed = e # choose a seed for next spider
			e.is_seed = True
			print "seed id = %s [%s]" % (e.id, e.__class__)
	print "++ %s entities, and %s of those were new ++" % (ncount, addcount)

def get_or_add(entity):
	"""if the entity is in the collection already, return the collected one. Otherwise add it to collection
	returns boolean added, and obj"""
	ekey = str(entity.__class__)
	if entities.has_key(ekey):
		for e in entities[ekey]:
			if e.matches(entity): return False, e
		entity.approve()
		entity.index = len(entities[ekey])
		entities[ekey].append(entity)
		posi.add_node(str(entity.__class__))
		return True, entity
	else:
		# first of its type
		entity.approve()
		entity.index = 0
		entities[ekey] = [entity]
		posi.add_node(str(entity.__class__))
		return True, entity

if __name__ == '__main__':
	util.log('INIT')
	spider()
	for e in entities:
		print dir(e)
