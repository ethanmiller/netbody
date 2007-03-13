from OpenGL.GL import *
from OpenGL.GLU import gluProject
import random, math, util, Image

class Attention:
	def __init__(self):
		self.read_body()
		self.indx = util.CONST.ATT_POS_INDX_START + 1 # next dest in points list
		self.pos = self.pts[util.CONST.ATT_POS_INDX_START]
		self.dest = self.pts[self.indx]
		self.inc = [(x[1] - x[0])/util.CONST.ATT_ANI_STEPS for x in zip(self.pos, self.dest)]

	def draw(self):
		glDisable(GL_TEXTURE_2D)
		glColor3f(*util.CONST.ATTCOLOR)
		glBlendFunc(GL_ONE, GL_ZERO)
		glPushMatrix()
		glTranslate(*self.pos)
		glBegin(GL_QUADS)
		self.cube()
		glEnd()
		glPopMatrix()
		self.set_screen_pos()
		if self.pos == self.dest:
			self.indx += 1
			if self.indx > self.ptct:
				self.indx %= self.ptct
			self.dest = self.pts[self.indx]
			self.inc = [(x[1] - x[0])/util.CONST.ATT_ANI_STEPS for x in zip(self.pos, self.dest)]
		self.pos = [x[0] + x[1] for x in zip(self.pos, self.inc)]
		#self.draw_dots()
		glEnable(GL_TEXTURE_2D)
		return self.pos

	def set_screen_pos(self):
		model = glGetDoublev(GL_MODELVIEW_MATRIX);
		proj = glGetDoublev(GL_PROJECTION_MATRIX);
		view = glGetIntegerv(GL_VIEWPORT);
		retx, rety, retz = gluProject(self.pos[0], self.pos[1], self.pos[2], model, proj, view)
		self.screenpos = (retx, util.CONST.VIZSIZE[1] - rety, retz)

	def cube(self):
		# Front Face 
		glVertex3f(0.0, 0.0, 1.0)	
		glVertex3f(1.0, 0.0, 1.0)
		glVertex3f(1.0, 1.0, 1.0)
		glVertex3f(0.0, 1.0, 1.0)	

		# Back Face
		glVertex3f(0.0, 0.0, 0.0)
		glVertex3f(0.0, 1.0, 0.0)	
		glVertex3f(1.0, 1.0, 0.0)	
		glVertex3f(1.0, 0.0, 0.0)	

		# Top Face
		glVertex3f(0.0, 1.0, 0.0)	
		glVertex3f(0.0, 1.0, 1.0)
		glVertex3f(1.0, 1.0, 1.0)	
		glVertex3f(1.0, 1.0, 0.0)	

		# Bottom Face       
		glVertex3f(0.0, 0.0, 0.0)
		glVertex3f(1.0, 0.0, 0.0)	
		glVertex3f(1.0, 0.0, 1.0)	
		glVertex3f(0.0, 0.0, 1.0)	

		# Right face
		glVertex3f(1.0, 0.0, 0.0)	
		glVertex3f(1.0, 1.0, 0.0)	
		glVertex3f(1.0, 1.0, 1.0)	
		glVertex3f(1.0, 0.0, 1.0)	

		# Left Face
		glVertex3f(0.0, 0.0, 0.0)	
		glVertex3f(0.0, 0.0, 1.0)	
		glVertex3f(0.0, 1.0, 1.0)	
		glVertex3f(0.0, 1.0, 0.0)	

	def draw_dots(self):
		glPushMatrix()
		glBegin(GL_POINTS)
		for pt in self.pts:
			glVertex3f(*pt)
		glEnd()
		glPopMatrix()

	def read_body(self):
		pf = open("resources/pts")
		# realines() on this file produces a list of strings in the format: '1,1,2\n'
		pts_tmp = [x[:-1].split(',') for x in pf.readlines() if not x.startswith('#')] 
		self.pts = [[int(y) for y in x] for x in pts_tmp]
		self.ptct = len(self.pts)-1

class Bit:
	def __init__(self, netdata):
		self.netdat = netdata
		self.pos = util.CONST.CENTER
		self.vec = [random.uniform(*util.CONST.BIT_SPEED_RANGE) for x in range(3)]
		self.deg = 0.0
		self.rotinc = random.uniform(*util.CONST.BIT_ROT_INC_RANGE)
		self.rotvec = [random.random() for x in range(3)]
		self.stuck = False
		self.stuckct = util.CONST.BIT_STUCK_LIMIT
		self.alpha = util.CONST.BIT_UNSTUCK_ALPHA
		# make image object with enough padding to get powers of 2 dimensions
		netimg = Image.open(netdata['img'])
		netimg = util.sizeimg(netimg)
		# netdat currently looks like:
		# {'imgid' : n, 'img' : '/path/to/image', 'words' : ['word1', 'word2']}
		# replace image path with image object
		self.netdat['img'] = netimg
		imgsize = (util.pow2(netimg.size[0]), util.pow2(netimg.size[1]))
		self.panelsize = (netimg.size[0], netimg.size[1])
		self.proportionalsize = (self.panelsize[0]/(imgsize[0]*1.0), self.panelsize[1]/(imgsize[1]*1.0))
		self.oimg = Image.new('RGB', imgsize, (0, 0, 0))
		self.oimg.paste(netimg, (0, 0))
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.oimg.size[0], self.oimg.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, self.oimg.tostring())
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

	def draw(self, atat):
		# atat = where attention is currently at
		glColor4f(1.0, 1.0, 1.0, self.alpha)
		if self.stuck:
			glBlendFunc(GL_ONE, GL_ZERO)
		else:
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glPushMatrix()
		glTranslate(*self.pos)
		glRotate(self.deg, *self.rotvec)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0); glVertex3f(0.0, 0.0, 0.0)
		glTexCoord2f(self.proportionalsize[0], 0.0); glVertex3f(self.panelsize[0]/15, 0.0, 0.0)
		glTexCoord2f(self.proportionalsize[0], self.proportionalsize[1]); glVertex3f(self.panelsize[0]/15, self.panelsize[1]/15, 0.0)
		glTexCoord2f(0.0, self.proportionalsize[1]); glVertex3f(0.0 , self.panelsize[1]/15, 0.0)
		glEnd()
		glPopMatrix()

		# do we update pos?
		if self.stuck:
			self.stuckct -= 1
			if self.stuckct == 0:
				#print 'unnstuck'
				self.stuckct = util.CONST.BIT_STUCK_LIMIT
				self.stuck = False
				self.alpha = util.CONST.BIT_UNSTUCK_ALPHA
			return
		dist = util.distance(self.pos, atat)
		if dist < 1.0:
			self.stuck = True
			self.alpha = 1.0
			return

		# update pos, rot
		self.pos = [x[0] + x[1] for x in zip(self.pos, self.vec)]
		self.deg += self.rotinc
		if self.deg > 360:
			self.deg %= 360
