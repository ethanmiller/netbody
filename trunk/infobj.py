from OpenGL.GL import *
import random, math

class Attention:
	def __init__(self):
		self.read_body()
		self.indx = 4901 # next dest in points list
		self.steps = 16.0 # how many places in between pts
		self.pos = self.pts[4900]
		self.dest = self.pts[4901]
		self.inc = [(x[1] - x[0])/self.steps for x in zip(self.pos, self.dest)]

	def draw(self):
		glColor3f(1.0, 0.0, 0.0)
		#glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (1.0, 0.0, 0.0, 1.0))
		#glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.0, 0.0, 0.0, 0.0))
		glBlendFunc(GL_ONE, GL_ZERO)
		glPushMatrix()
		glTranslate(*self.pos)
		glBegin(GL_QUADS)
		self.cube()
		glEnd()
		glPopMatrix()
		#print self.pos, self.dest
		if self.pos == self.dest:
			self.indx += 1
			if self.indx > self.ptct:
				self.indx %= self.ptct
			self.dest = self.pts[self.indx]
			self.inc = [(x[1] - x[0])/self.steps for x in zip(self.pos, self.dest)]
		self.pos = [x[0] + x[1] for x in zip(self.pos, self.inc)]
		#self.draw_dots()
		return self.pos

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
		self.pos = [50.0, 50.0, 23.0]
		self.vec = [random.uniform(-0.005, 0.005) for x in range(3)]
		self.deg = 0.0
		self.rotvec = [random.random() for x in range(3)]
		self.stuck = False
		self.stucklimit = 50000
		self.stuckct = self.stucklimit
		self.alpha = 0.2
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
				self.stuckct = self.stucklimit
				self.stuck = False
				self.alpha = 0.2
			return
		diff = [x[1]-x[0] for x in zip(self.pos, atat)]
		dist = math.sqrt(reduce(lambda x, y: x+y, [z*z for z in diff]))
		if dist < 1.0:
			#print 'ehh stuck'
			self.stuck = True
			self.alpha = 1.0
			return

		# update pos, rot
		self.pos = [x[0] + x[1] for x in zip(self.pos, self.vec)]
		self.deg += 1.5
		if self.deg > 360:
			self.deg %= 360
