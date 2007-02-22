from UserList import UserList
from OpenGL.GL import *
class Body:
	def __init__(self):
		self.body_pts = []
		self.read_body()
	
	def draw(self):
		glColor3f(1.0, 1.0, 1.0)
		glBegin(GL_POINTS)
		for pt in self.body_pts:
			pt.draw()

		glEnd();				

	def read_body(self):
		pf = open("pts")
		# realines() on this file produces a list of strings in the format: '1.000000 1.0000000 2.000000\n'
		body_pts_tmp = [x[:-1].split(' ') for x in pf.readlines()] 
		for pt in body_pts_tmp:
			self.body_pts.append(BodyPoint([float(x) for x in pt]))
		# zsort so that we go from the head down
		self.body_pts.sort(cmp=lambda x,y: int(y[2]*1000)-int(x[2]*1000))
		

class BodyPoint(UserList):
	def __init__(self, xyz):
		self.data = xyz
	def draw(self):
		glVertex3f(*self.data)
