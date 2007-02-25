from UserList import UserList
from OpenGL.GL import *
class Body:
	def __init__(self, scale, orig, dest):
		# orig and dest are just y,z points - we're not altering the x positions
		self.set_vars(scale, orig, dest)
		self.body_pts = []
		self.read_body()

	def set_vars(self, s, orig, dest, pos=None):
		self.scale = s
		self.init = orig
		self.dest = dest
		self.ctl = (dest[0], orig[1]) # control point for trajectory curve
		self.pos = pos
		if not pos:	
			self.pos = orig
	
	def draw(self):
		glColor3f(1.0, 1.0, 1.0)
		glPushMatrix()
		glRotatef(270.0,1.0,0.0,0.0)
		glTranslatef(0.0, self.pos[0], self.pos[1]*self.scale)
		glScalef(self.scale, self.scale, self.scale)
		glBegin(GL_POINTS)
		for pt in self.body_pts:
			pt.draw()

		glEnd();				
		glPopMatrix()

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


# def load_textures():
	# texturefile = os.path.join('data','nehe.bmp')
	# textureSurface = pygame.image.load(texturefile)
	# textureData = pygame.image.tostring(textureSurface, "RGBX", 1)
	# 
	# glBindTexture(GL_TEXTURE_2D, textures[0])
	# glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, textureSurface.get_width(), textureSurface.get_height(), 0,
		# GL_RGBA, GL_UNSIGNED_BYTE, textureData );
	# glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
	# glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
