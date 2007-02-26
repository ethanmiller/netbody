from UserList import UserList
from OpenGL.GL import *
import random, math
class Body:
	def __init__(self, scale, orig, dest):
		# orig and dest are just y,z points - we're not altering the x positions
		self.set_vars(scale, orig, dest)
		self.body_pts = []
		# when the body is scaled up, only the "lanscape" area is visible
		self.landscape = scale > 1.0
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
		for pt in self.body_pts:
			pt.draw()
		glPopMatrix()

	def read_body(self):
		pf = open("pts")
		crownpts = 81 # how many of thes points constitute the top  of the head
		platformpts = 145 # how many points make up the "landscape"
		# realines() on this file produces a list of strings in the format: '1.000000 1.0000000 2.000000\n'
		body_pts_tmp = [x[:-1].split(' ') for x in pf.readlines()] 
		body_pts_tmp = [[float(y) for y in x] for x in body_pts_tmp]
		# zsort so that we go from the head down
		body_pts_tmp.sort(cmp=lambda x,y: int(y[2]*1000)-int(x[2]*1000))
		for count, pt in enumerate(body_pts_tmp):
			if count < crownpts:
				n = 2
			elif crownpts <= count < platformpts+crownpts:
				n = 1
			else:
				n = 0
			self.body_pts.append(BodyPoint(pt, n, self.landscape))
		
class BodyPoint(UserList):
	def __init__(self, xyz, type, landscape_mode):
		self.data = xyz
		# pt_type : 0 = regular body point, 1 = "landscape" point, 2 = crown point
		self.pt_type = type
		self.images = [ImagePlane(self.data, type==2 and landscape_mode, type==1) for x in range(1)]
	
	def draw(self):
		for i in self.images:
			#TBD use landscape_mode info
			i.draw()

class ImagePlane:
	def __init__(self, dest, anim, landscape):
		self.anim = anim
		rand_range = 0.5
		self.dest = [random.uniform(x-rand_range, x+rand_range) for x in dest]
		self.angle = random.random()*360
		self.rotvec = [random.random() for x in range(3)]
		if anim:
			self.pos = (0.0, 0.0, -5.14)
			self.scale = 0.002 # 1/500th - this will scale up as it moves to it's destination...
		else:
			self.pos = self.dest
			if landscape:
				# scale so that we're smaller closer to center
				max = 1.1 # based on the current body model
				dist = math.sqrt(dest[0]*dest[0] + dest[1]*dest[1])			
				# two points (max, 1.0), (0, .002)
				slope = 0.998/max
			else:
				self.scale = 1.0

	def draw(self):
		glPushMatrix()
		glTranslatef(*self.pos)
		glRotatef(self.angle, *self.rotvec)
		glBegin(GL_LINE_STRIP)
		# doing a 3x4 rec for now
		glVertex3f(0.0, 0.0, 0.0)
		glVertex3f(0.3, 0.0, 0.0)
		glVertex3f(0.3, 0.4, 0.0)
		glVertex3f(0.0, 0.4, 0.0)
		glVertex3f(0.0, 0.0, 0.0)
		glEnd()
		glPopMatrix()


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
