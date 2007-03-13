from OpenGL.GL import *
import util, time, Image, ImageDraw, ImageFont, math

class Panel:
	def __init__(self):
		self.font = ImageFont.truetype('resources/FreeSans.ttf', 16)
		self.textures = glGenTextures(2)
		self.imgids = []
		self.imgrealheight = 0
		self.imgpanelsize = [util.pow2(util.CONST.IPANEL_WIDTH), util.pow2(util.CONST.VIZSIZE[1])]
		self.imgpanel = Image.new('RGB', (self.imgpanelsize[0], self.imgpanelsize[1]), util.CONST.PANEL_BG)
		self.imgoffset = 0.0
		self.retexture = True
		self.wordrealsize = 0
		self.wordpanelsize = [util.pow2(util.CONST.VIZSIZE[0]), util.pow2(util.CONST.WPANEL_HEIGHT)]
		self.wordpanel = Image.new('RGB', (self.wordpanelsize[0], self.wordpanelsize[1]), util.CONST.PANEL_BG)
		self.wordoffset = 0

	def draw(self, dat, atat):
		for d in dat:
			if d['imgid'] not in self.imgids:
				self.addimagewords(d)
				self.imgids.append(d['imgid'])
		self.draw_images()
		self.draw_words()

	def draw_images(self):
		glBindTexture(GL_TEXTURE_2D, self.textures[0])
		if self.retexture:
			strrep = self.imgpanel.tostring()
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.imgpanel.size[0], self.imgpanel.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, strrep)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		panelheight = util.CONST.VIZSIZE[1] - util.CONST.IPANEL_PADDING * 2
		propytop = 0.0
		if self.imgoffset > 0.0:
			propytop = (self.imgoffset*1.0)/self.imgpanel.size[1]
		glColor4f(1.0, 1.0, 1.0, 1.0)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, propytop)
		##print (0.0, propytop)
		glVertex2f(util.CONST.IPANEL_PADDING, util.CONST.IPANEL_PADDING)
		glTexCoord2f(util.CONST.IPANEL_WIDTH/(self.imgpanel.size[0]*1.0), propytop)
		#print (util.CONST.IPANEL_WIDTH/(self.imgpanel.size[0]*1.0), propytop)
		glVertex2f(util.CONST.IPANEL_WIDTH + util.CONST.IPANEL_PADDING, util.CONST.IPANEL_PADDING)
		glTexCoord2f(util.CONST.IPANEL_WIDTH/(self.imgpanel.size[0]*1.0), (panelheight+self.imgoffset*1.0)/self.imgpanel.size[1])
		#print (util.CONST.IPANEL_WIDTH/(self.imgpanel.size[0]*1.0), (panelheight+self.imgoffset*1.0)/self.imgpanel.size[1])
		glVertex2f(util.CONST.IPANEL_WIDTH + util.CONST.IPANEL_PADDING, panelheight)
		glTexCoord2f(0.0, (panelheight+self.imgoffset*1.0)/self.imgpanel.size[1])
		#print (0.0, (panelheight+self.imgoffset*1.0)/self.imgpanel.size[1])
		#print '\n'
		glVertex2f(util.CONST.IPANEL_PADDING,  panelheight)
		glEnd()
		if self.imgoffset > 0:
			if self.imgoffset < 0.2:
				self.imgoffset = 0.0
				# chop off the image if it has gotten long
				self.imgpanelsize[1] = util.CONST.VIZSIZE[1]
				self.imgrealheight = self.imgpanelsize[1]
			else:
				self.imgoffset -= self.imgoffset/6.0

	def draw_words(self):
		glBindTexture(GL_TEXTURE_2D, self.textures[1])
		if self.retexture:
			strrep = self.wordpanel.tostring()
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.wordpanel.size[0], self.wordpanel.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, strrep)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			self.retexture = False
		panelwidth = util.CONST.VIZSIZE[0] - util.CONST.WPANEL_PADDING * 2
		propx = 0.0
		if self.wordoffset > 0.0:
			propx = (self.wordoffset*1.0)/self.wordpanel.size[0]
		glColor4f(1.0, 1.0, 1.0, 1.0)
		glBegin(GL_QUADS)
		glTexCoord2f(propx, 0.0)
		glVertex2f(util.CONST.WPANEL_PADDING, util.CONST.VIZSIZE[1]-util.CONST.WPANEL_PADDING-util.CONST.WPANEL_HEIGHT)
		glTexCoord2f((panelwidth+self.wordoffset)/self.wordpanel.size[0], 0.0)
		glVertex2f(panelwidth, util.CONST.VIZSIZE[1]-util.CONST.WPANEL_PADDING-util.CONST.WPANEL_HEIGHT)
		glTexCoord2f((panelwidth+self.wordoffset)/self.wordpanel.size[0], util.CONST.WPANEL_HEIGHT/(self.wordpanel.size[1]*1.0))
		glVertex2f(panelwidth, util.CONST.VIZSIZE[1]-util.CONST.WPANEL_PADDING)
		glTexCoord2f(propx, util.CONST.WPANEL_HEIGHT/(self.wordpanel.size[1]*1.0))
		glVertex2f(util.CONST.WPANEL_PADDING, util.CONST.VIZSIZE[1]-util.CONST.WPANEL_PADDING)
		glEnd()
		if self.wordoffset > 0:
			if self.wordoffset < 0.2:
				self.wordoffset = 0.0
				# chop
				self.wordpanelsize[0] = util.CONST.VIZSIZE[0]
				self.wordrealsize = self.wordpanelsize[0]
			else:
				self.wordoffset -= self.wordoffset/6.0

	def addimagewords(self, d):
		# reset textures??
		glDeleteTextures(self.textures)
		self.textures = glGenTextures(2)
		# --------- image ----------------
		self.imgrealheight += d['img'].size[1]
		self.imgpanelsize[1] = util.pow2(self.imgrealheight)
		while self.imgpanelsize[1] < (util.CONST.VIZSIZE[1] + self.imgoffset):
			self.imgpanelsize[1] = util.pow2(self.imgpanelsize[1] + 1) # round up to the next power of 2
		#*** bites it any larger than 2048
		if self.imgpanelsize[1] > 2048:
			self.imgpanelsize[1] = 2048
		#this is a blank panel with the new image height added
		tmppanel = Image.new('RGB', (self.imgpanelsize[0], self.imgpanelsize[1]), util.CONST.PANEL_BG)
		#paste the new image first, and the old set below that.
		tmppanel.paste(d['img'], (0,0))
		tmppanel.paste(self.imgpanel, (0, d['img'].size[1]))
		self.imgpanel = tmppanel
		self.imgoffset += d['img'].size[1]*1.0
		# ----------- words -------------
		wordimgs = []
		tmppanel = Image.new('RGB', (8, 8), (0.0, 0.0, 0.0)) # using this just to get textsize
		drawr = ImageDraw.Draw(tmppanel)
		newwordwidth = 0
		for w in d['words']:	
			wit = drawr.textsize(w, font=self.font)
			newwordwidth = newwordwidth + wit[0] + util.CONST.WORD_PADDING
			# now that I know the size, I can build it
			wim = Image.new('RGB', (wit[0]+2, wit[1]+2), util.CONST.PANEL_BG)
			dr = ImageDraw.Draw(wim)
			dr.text((1, 1), w, font=self.font, fill=0)
			wordimgs.append(wim)
		# ok - now the tmppanel
		self.wordrealsize += newwordwidth
		self.wordpanelsize[0] = util.pow2(int(self.wordrealsize))
		while self.wordpanelsize[0] < (util.CONST.VIZSIZE[0] + self.wordoffset):
			self.wordpanelsize[0] = util.pow2(self.wordpanelsize[0] + 1)
		#*** bites it any larger than 2048
		if self.wordpanelsize[0] > 2048:
			self.wordpanelsize[0] = 2048
		tmppanel = Image.new('RGB', (self.wordpanelsize[0], self.wordpanelsize[1]), util.CONST.PANEL_BG)
		wordx = 0.0
		for wi in wordimgs:
			tmppanel.paste(wi, (int(wordx), 5))
			wordx = wordx + wi.size[0] + util.CONST.WORD_PADDING
		# paste the old image
		tmppanel.paste(self.wordpanel, (int(wordx), 0))
		self.wordpanel = tmppanel
		self.wordoffset += newwordwidth
		# ---- retexture ----	
		self.retexture = True
