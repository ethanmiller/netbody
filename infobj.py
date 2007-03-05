from OpenGL.GL import *
from OpenGL.GLU import gluProject
import random, math, util

class Attention:
	def __init__(self):
		self.read_body()
		self.indx = util.CONST.ATT_POS_INDX_START + 1 # next dest in points list
		self.pos = self.pts[util.CONST.ATT_POS_INDX_START]
		self.dest = self.pts[self.indx]
		self.inc = [(x[1] - x[0])/util.CONST.ATT_ANI_STEPS for x in zip(self.pos, self.dest)]

	def draw(self):
		glColor3f(*util.CONST.ATTCOLOR)
		#glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (1.0, 0.0, 0.0, 1.0))
		#glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.0, 0.0, 0.0, 0.0))
		glBlendFunc(GL_ONE, GL_ZERO)
		glPushMatrix()
		glTranslate(*self.pos)
		glBegin(GL_QUADS)
		self.cube()
		glEnd()
		glPopMatrix()
		self.set_screen_pos()
		#print self.pos, self.dest
		if self.pos == self.dest:
			self.indx += 1
			if self.indx > self.ptct:
				self.indx %= self.ptct
			self.dest = self.pts[self.indx]
			self.inc = [(x[1] - x[0])/util.CONST.ATT_ANI_STEPS for x in zip(self.pos, self.dest)]
		self.pos = [x[0] + x[1] for x in zip(self.pos, self.inc)]
		#self.draw_dots()
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
		pf = open("pts")
		# realines() on this file produces a list of strings in the format: '1,1,2\n'
		pts_tmp = [x[:-1].split(',') for x in pf.readlines() if not x.startswith('#')] 
		self.pts = [[int(y) for y in x] for x in pts_tmp]
		self.ptct = len(self.pts)-1

class Bit:
	def __init__(self, data):
		# TODO connect data
		self.pos = util.CONST.CENTER
		self.vec = [random.uniform(*util.CONST.BIT_TRAJ_VEC_RANGE) for x in range(3)]
		self.deg = 0.0
		self.rotinc = random.uniform(*util.CONST.BIT_ROT_INC_RANGE)
		self.rotvec = [random.random() for x in range(3)]
		self.stuck = False
		self.stuckct = util.CONST.BIT_STUCK_LIMIT
		self.alpha = util.CONST.BIT_UNSTUCK_ALPHA
		#len = math.sqrt(reduce(lambda x, y: x+y, [x*x for x in self.vec]))
		#self.vec = [x/len for x in self.vec]
		#self.rate = 

	def draw(self, atat):
		# atat = where attention is currently at
		glColor4f(0.4, 1.0, 0.1, self.alpha)
		#glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.0, 1.0, 0.0, self.alpha))
		#glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 0.0))
		#glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 0.0))
		if self.stuck:
			glBlendFunc(GL_ONE, GL_ZERO)
		else:
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glPushMatrix()
		glTranslate(*self.pos)
		glRotate(self.deg, *self.rotvec)
		glBegin(GL_QUADS)
		glVertex3f(0.0, 0.0, 0.0)
		glVertex3f(1.0, 0.0, 0.0)
		glVertex3f(1.0, 1.0, 0.0)
		glVertex3f(0.0, 1.0, 0.0)
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
		#diff = [x[1]-x[0] for x in zip(self.pos, atat)]
		#dist = math.sqrt(reduce(lambda x, y: x+y, [z*z for z in diff]))
		dist = util.distance(self.pos, atat)
		if dist < 1.0:
			#print 'ehh stuck'
			self.stuck = True
			self.alpha = 1.0
			return

		# update pos, rot
		self.pos = [x[0] + x[1] for x in zip(self.pos, self.vec)]
		self.deg += self.rotinc
		if self.deg > 360:
			self.deg %= 360
