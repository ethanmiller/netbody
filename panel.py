from OpenGL.GL import *
import util, time, Image, ImageDraw, ImageFont, math

class Panel:
	def __init__(self):
		self.font = ImageFont.truetype('resources/NewMedia.ttf', 12)
		self.imgtex = glGenTextures(1)
		self.imgids = []
		self.imgwidth = util.pow2(util.CONST.PANEL_WIDTH)
		self.imgheight = 0
		self.imgpanel = Image.new('RGB', (self.imgwidth, util.pow2(util.CONST.VIZSIZE[1])), util.CONST.PANEL_BG)
		self.imgoffset = 0
		self.imgretex = True
		self.wordpanel = None

	def draw(self, dat, atat):
		for d in dat:
			if d['imgid'] not in self.imgids:
				self.addimagewords(d)
				self.imgids.append(d['imgid'])
		self.draw_images()
		self.draw_words()

	def draw_images(self):
		glBindTexture(GL_TEXTURE_2D, self.imgtex)
		if self.imgretex:
			strrep = self.imgpanel.tostring()
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.imgpanel.size[0], self.imgpanel.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, strrep)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			self.imgretex = False
		panelheight = util.CONST.VIZSIZE[1] - util.CONST.PANEL_PADDING * 2
		propytop = 0.0
		if self.imgoffset > 0.0:
			propytop = (self.imgoffset*1.0)/self.imgpanel.size[1]
		glColor4f(1.0, 1.0, 1.0, 1.0)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, propytop)
		glVertex2f(util.CONST.PANEL_PADDING, util.CONST.PANEL_PADDING)
		glTexCoord2f(util.CONST.PANEL_WIDTH/(self.imgpanel.size[0]*1.0), propytop)
		glVertex2f(util.CONST.PANEL_WIDTH + util.CONST.PANEL_PADDING, util.CONST.PANEL_PADDING)
		glTexCoord2f(util.CONST.PANEL_WIDTH/(self.imgpanel.size[0]*1.0), (panelheight+self.imgoffset)/self.imgpanel.size[1])
		glVertex2f(util.CONST.PANEL_WIDTH + util.CONST.PANEL_PADDING, panelheight)
		glTexCoord2f(0.0, (panelheight+self.imgoffset)/self.imgpanel.size[1])
		glVertex2f(util.CONST.PANEL_PADDING,  panelheight)
		glEnd()
		if self.imgoffset > 0:
			if self.imgoffset < 0.2:
				self.imgoffset = 0.0
				# chop off the image if it has gotten long
				self.imgsize = util.CONST.VIZSIZE[1]
			else:
				self.imgoffset -= self.imgoffset/6.0

	def draw_words(self):
		pass

	def addimagewords(self, d):
		self.imgheight += d['img'].size[1]
		minh = int(math.ceil(self.imgheight))
		if (minh - self.imgoffset) < util.CONST.VIZSIZE[1]:
			minh = int(math.ceil(util.CONST.VIZSIZE[1] + self.imgoffset + d['img'].size[1]))
		#this is a blank panel with the new image height added
		tmppanel = Image.new('RGB', (self.imgwidth, util.pow2(minh)), util.CONST.PANEL_BG)
		#paste the new image first, and the old set below that.
		tmppanel.paste(d['img'], (0,0))
		tmppanel.paste(self.imgpanel, (0, d['img'].size[1]))
		self.imgpanel = tmppanel
		self.imgoffset += d['img'].size[1]
		self.imgretex = True

		#at_xdiff = atat[0] - util.CONST.PANEL_WIDTH
		#glBegin(GL_LINE_STRIP)
		#glVertex3f(util.CONST.PANEL_WIDTH, 430.0, 0.0)
		#glVertex3f(at_xdiff/2.0 + util.CONST.PANEL_WIDTH, 430.0, 0.0)
		#glVertex3f(at_xdiff/2.0 + util.CONST.PANEL_WIDTH, atat[1], 0.0)
		#glVertex3f(*atat)
		#glEnd()

		#stime = time.strftime('%a, %b %d %H:%M:%S')
		#im = Image.new('RGB', (128, 32), (255, 255, 255))
		#drawr = ImageDraw.Draw(im)
		#drawr.text((5, 15), stime, font=self.font, fill=0)

		#glBindTexture(GL_TEXTURE_2D, self.time_tex)
		#glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.size[0], im.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, im.tostring())
		#glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		#glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		#glBegin(GL_QUADS)
		#glTexCoord2f(0.0, 0.0); glVertex3f(5.0, 408.0, 0.0)
		#glTexCoord2f(1.0, 0.0); glVertex3f(133.0, 408.0, 0.0)
		#glTexCoord2f(1.0, 1.0); glVertex3f(133.0, 440.0, 0.0)
		#glTexCoord2f(0.0, 1.0); glVertex3f(5, 440.0, 0.0)
		#glEnd()

