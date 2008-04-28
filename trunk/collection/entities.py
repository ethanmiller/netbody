import base, util, apis.flickr, apis.delic, apis.technorati, apis.youtube
import random, datetime, urllib2, socket, os, cairo, time

socket.setdefaulttimeout(15)

class Image(base.Entity):
	def __init__(self, **kwargs):
		base.Entity.__init__(self, ['img_link', 'author_id', 'username', 'title', 'tags'], **kwargs)
		self.id = kwargs['img_link']
		# username attr came in the form "nobody@flickr.com (username)"
		self.username = self.username.split('(')[1][:-1]
		# taglist is space separated, unless it's a list alerady
		if type(self.tags) != list : self.tags = self.tags.split(' ')
		self.im = None
		self.status = 200

	def approve(self):
		img_file_path = apis.flickr.dl_image(apis.flickr.photo_url(self.img_link))
		if img_file_path == None:
			self.spiderable = False
			self.status = 400
			self.im = cairo.ImageSurface.create_from_png(util.CONST.PICERR_PATH)
		else:
			self.im = cairo.ImageSurface.create_from_png(img_file_path)
		self.ext_width = self.im.get_width() + util.CONST.BOX_MARGIN*2
		self.ext_height = self.im.get_height() + util.CONST.BOX_MARGIN*2

	def spider(self):
		''' When Image inits, we already have a tag list and the username - create obj based on that...'''
		ret = []
		# could have gobs of tags..
		for t in random.sample(self.tags, min(len(self.tags), 3)):
			t = t.strip()
			if len(t) > 1 : ret.append(Tag(tag=t))
		dnames = {'flickr_display' : self.username, 'flickr_id' : self.author_id}
		urlname = self.img_link.split("/")[4]
		if urlname != self.author_id : dnames['flickr_url'] = urlname
		ret.append(UserName(names=dnames))
		print "--- an Image (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

	def draw(self, ctx):
		pos = base.posi.get_pos(str(self.__class__), self.index)
		posx, posy = pos.xy()
		base.Entity.draw(self, ctx)
		if self.width <= util.CONST.ENTITY_DEFAULT_SIZE*3 and self.height <= util.CONST.ENTITY_DEFAULT_SIZE*3: return
		sc = self.width/self.ext_width*1.0
		ctx.translate(posx + util.CONST.BOX_MARGIN*sc, posy + util.CONST.BOX_MARGIN*sc)
		ctx.scale(sc, sc)
		ctx.set_source_surface(self.im)
		ctx.paint()
		ctx.scale(1/sc, 1/sc)
		ctx.translate(-posx - util.CONST.BOX_MARGIN*sc, -posy - util.CONST.BOX_MARGIN*sc)
			

class Tag(base.Entity):
	""" Tag Entity just expects a 'tag' argument in constructor """
	def __init__(self, **kwargs):
		base.Entity.__init__(self, ['tag'], **kwargs)
		self.id = kwargs['tag']
		# places to store results from api calls
		self.api_res_flickr = []
		self.api_res_delic = []
		self.api_res_tech = []
		self.api_res_yt = []

	def set_extent(self, ctx):
		width, height = ctx.text_extents(self.tag)[2:4]
		self.ext_width = width + util.CONST.BOX_MARGIN*2
		self.ext_height = height + util.CONST.BOX_MARGIN*2

	def spider(self):
		ret = []
		# currently 1 random samples from each of these...
		limit_to = 3
		yt_limit_to = 1
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
		for i in range(min(yt_limit_to, len(self.api_res_yt))):
			yt = self.api_res_yt.pop(0)
			tgs = ''
			if yt.has_key('media_category'): 
				tgs = yt['media_category']
			elif yt.has_key('tags'):
				tgs = yt['tags'][0]['term']
			ret.append(Video(url=yt['link'], title=yt['title'], username=yt['author_detail']['name'], tags=tgs))
		print "--- a Tag (%s) spiders %s other entities..." % (self.tag, len(ret))
		return ret

	def draw(self, ctx):
		ctx.set_font_size(util.CONST.TAG_TEXT_SIZE)
		if not self.extent_set : self.set_extent(ctx)
		base.Entity.draw(self, ctx) # let base class draw the square
		if self.width == util.CONST.ENTITY_DEFAULT_SIZE and self.height == util.CONST.ENTITY_DEFAULT_SIZE: return
		# calc the proportion for scaling by width
		ctx.set_source_rgb(*util.CONST.TAG_TXT_COLOR)
		sc = self.width/self.ext_width*1.0
		x_bearing, y_bearing, w, h = ctx.text_extents(self.tag)[:4]
		pos = base.posi.get_pos(str(self.__class__), self.index)
		posx, posy = pos.xy()
		ctx.move_to(posx + util.CONST.BOX_MARGIN*sc - x_bearing*sc, posy + util.CONST.BOX_MARGIN*sc - y_bearing*sc)
		ctx.scale(sc, sc)
		ctx.show_text(self.tag)
		ctx.scale(1/sc, 1/sc)

class BlogPost(base.Entity):
	def __init__(self, **kwargs):
		base.Entity.__init__(self, ['blog_link', 'title', 'summary'], **kwargs)
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
		###### temp
		self.ext_width = 80
		self.ext_height = 25

	def set_extent(self, ctx):
		width, height = ctx.text_extents(self.title)[2:4]
		self.ext_width = width + util.CONST.BOX_MARGIN*2
		self.ext_height = height + util.CONST.BOX_MARGIN*2

	def spider(self):
		import apis.yahoo
		ret = []
		# summary gave us a little text description of the blog post...
		# yahoo term extration gets 'keywords' out of that...
		for term in apis.yahoo.termExtraction(self.summary)[:3]:
			for t in term.split(' '):
				t = t.strip()
				if len(t) > 1 and t not in util.CONST.NOISE_WORDS: ret.append(Tag(tag=t))
		print "--- a BlogPost (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

	def draw(self, ctx):
		ctx.set_font_size(util.CONST.BLOG_TEXT_SIZE)
		if not self.extent_set : self.set_extent(ctx)
		base.Entity.draw(self, ctx) # let base class draw the square
		if self.width == util.CONST.ENTITY_DEFAULT_SIZE and self.height == util.CONST.ENTITY_DEFAULT_SIZE: return
		# calc the proportion for scaling by width
		ctx.set_source_rgb(*util.CONST.BLOG_TXT_COLOR)
		sc = self.width/self.ext_width*1.0
		x_bearing, y_bearing, w, h = ctx.text_extents(self.title)[:4]
		pos = base.posi.get_pos(str(self.__class__), self.index)
		posx, posy = pos.xy()
		ctx.move_to(posx + util.CONST.BOX_MARGIN*sc - x_bearing*sc, posy + util.CONST.BOX_MARGIN*sc - y_bearing*sc)
		ctx.scale(sc, sc)
		ctx.show_text(self.title)
		ctx.scale(1/sc, 1/sc)

class UserName(base.Entity):
	def __init__(self, **kwargs):
		base.Entity.__init__(self, ['names'], **kwargs)
		self.id = reduce(lambda n, n2 : n + n2, self.names.values()) # just has to be a unique id
		self.display_name = self.names[self.names.keys()[0]]
		if self.names.has_key('flickr_display'): self.display_name = self.names['flickr_display']
		self.limit_to = 4

	class api_res:
		class flickr:
			socnet = []
			images = []
		class delic:
			socnet = []
			links = []
		class yt:
			vids = []

	def set_extent(self, ctx):
		width, height = ctx.text_extents(util.CONST.UNAME_LABEL + self.display_name)[2:4]
		self.ext_width = width + util.CONST.BOX_MARGIN*2
		self.ext_height = height + util.CONST.BOX_MARGIN*2

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

	def draw(self, ctx):
		ctx.set_font_size(util.CONST.UNAME_TEXT_SIZE)
		if not self.extent_set : self.set_extent(ctx)
		base.Entity.draw(self, ctx) # let base class draw the square
		if self.width == util.CONST.ENTITY_DEFAULT_SIZE and self.height == util.CONST.ENTITY_DEFAULT_SIZE: return
		# calc the proportion for scaling by width
		ctx.set_source_rgb(*util.CONST.USER_TXT_COLOR)
		sc = self.width/self.ext_width*1.0
		x_bearing, y_bearing, w, h = ctx.text_extents(self.display_name)[:4]
		pos = base.posi.get_pos(str(self.__class__), self.index)
		posx, posy = pos.xy()
		ctx.move_to(posx + util.CONST.BOX_MARGIN*sc - x_bearing*sc, posy + util.CONST.BOX_MARGIN*sc - y_bearing*sc)
		ctx.scale(sc, sc)
		ctx.show_text(util.CONST.UNAME_LABEL + self.display_name)
		ctx.scale(1/sc, 1/sc)
	
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
			tgs = ''
			if yt.has_key('media_category'): 
				tgs = yt['media_category']
			elif yt.has_key('tags'):
				tgs = yt['tags'][0]['term']
			ret.append(Video(url=yt['link'], title=yt['title'], username=yt['author_detail']['name'], tags=tgs))
		self.network_count = self.network_count + len(ret)
		return ret

class Link(base.Entity):
	def __init__(self, **kwargs):
		base.Entity.__init__(self, ['url', 'title'], **kwargs)
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

	def set_extent(self, ctx):
		width, height = ctx.text_extents(self.title)[2:4]
		self.ext_width = width + util.CONST.BOX_MARGIN*2
		self.ext_height = height + util.CONST.BOX_MARGIN*2

	def spider(self):
		ret = []
		limit_to = 3
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

	def draw(self, ctx):
		ctx.set_font_size(util.CONST.LINK_TEXT_SIZE)
		if not self.extent_set : self.set_extent(ctx)
		base.Entity.draw(self, ctx) # let base class draw the square
		if self.width == util.CONST.ENTITY_DEFAULT_SIZE and self.height == util.CONST.ENTITY_DEFAULT_SIZE: return
		# calc the proportion for scaling by width
		ctx.set_source_rgb(*util.CONST.LINK_TXT_COLOR)
		sc = self.width/self.ext_width*1.0
		x_bearing, y_bearing, w, h = ctx.text_extents(self.title)[:4]
		pos = base.posi.get_pos(str(self.__class__), self.index)
		posx, posy = pos.xy()
		ctx.move_to(posx + util.CONST.BOX_MARGIN*sc - x_bearing*sc, posy + util.CONST.BOX_MARGIN*sc - y_bearing*sc)
		ctx.scale(sc, sc)
		ctx.show_text(self.title)
		ctx.scale(1/sc, 1/sc)

class Video(base.Entity):
	def __init__(self, **kwargs):
		import urlparse
		base.Entity.__init__(self, ['url', 'title', 'username', 'tags'], **kwargs)
		q = urlparse.urlparse(self.url)[4]
		self.id = q.split("=")[1]
		self.status = 200
		if type(self.tags) == str : 
			if self.tags.strip() == '':
				self.spiderable = False
			else:
				self.tags = self.tags.split(' ')
		self.proc_stage = 0
		self.dl = None
		self.splitvid = None
		self.splitaud = None
		self.im = None
		self.vid_indx = 0
		self.img_set = []
		self.vid_launched = False

	def approve(self):
		# pretty much have to wait till we get to stage two here - won't have any images to work with till then
		while self.proc_stage < 2:
			if self.proc_stage == -1: break
			self.proc_files()
			print ">>>> waiting for yt video %s" % self.title
			time.sleep(3)
		self.set_next_frame()
		self.ext_width = self.im.get_width() + util.CONST.BOX_MARGIN*2
		self.ext_height = self.im.get_height() + util.CONST.BOX_MARGIN*2

	def set_next_frame(self):
		if self.proc_stage == -1:
			if not self.im: self.im = cairo.ImageSurface.create_from_png(util.CONST.PICERR_PATH)
			return
		if not self.img_set:
			path = os.path.join('resources', 'videos', self.id)
			self.img_set = [os.path.join(path, x) for x in os.listdir(path) if x.endswith('png')]
			self.img_set.sort()
			if not self.img_set:
				# seems some videos can't be split
				if not self.im: self.im = cairo.ImageSurface.create_from_png(util.CONST.PICERR_PATH)
				return
		self.im = cairo.ImageSurface.create_from_png(self.img_set[self.vid_indx])
		self.vid_indx = (self.vid_indx + 1) % len(self.img_set)
	
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
		for t in random.sample(self.tags, min(len(self.tags), 3)):
			t = t.strip()
			if len(t) > 1 : ret.append(Tag(tag=t))
		ret.append(UserName(names={'youtube' : self.username}))
		print "--- a YouTube Vid (%s) spiders %s other entities..." % (self.title, len(ret))
		return ret

	def draw(self, ctx):
		pos = base.posi.get_pos(str(self.__class__), self.index)
		posx, posy = pos.xy()
		base.Entity.draw(self, ctx)
		if self.width <= util.CONST.ENTITY_DEFAULT_SIZE*3 and self.height <= util.CONST.ENTITY_DEFAULT_SIZE*3: return
		if not self.vid_launched:
			util.log(os.path.join('resources', 'videos', self.id, 'audio.mp3'))
			self.vid_launched = True
		sc = self.width/self.ext_width*1.0
		ctx.translate(posx + util.CONST.BOX_MARGIN*sc, posy + util.CONST.BOX_MARGIN*sc)
		ctx.scale(sc, sc)
		ctx.set_source_surface(self.im)
		ctx.paint()
		ctx.scale(1/sc, 1/sc)
		ctx.translate(-posx - util.CONST.BOX_MARGIN*sc, -posy - util.CONST.BOX_MARGIN*sc)
		self.set_next_frame()
