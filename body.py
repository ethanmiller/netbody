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
		if type == 1:
			self.images = [ImagePlane(self.data, type==2 and landscape_mode, type==1) for x in range(1)]
		else:
			self.images = [ImagePlane(self.data, type==2 and landscape_mode, type==1) for x in range(5)]
	
	def draw(self):
		for i in self.images:
			#TBD use landscape_mode info
			i.draw()

class ImagePlane:
	def __init__(self, dest, anim, landscape):
		self.anim = anim
		rand_range = 0.005
		self.dest = [random.uniform(x-rand_range, x+rand_range) for x in dest]
		self.angle = random.random()*360
		self.rotvec = [random.random() for x in range(3)]
		self.color = (1.0, 1.0, 1.0, 0.5)
		if anim:
			self.pos = (0.0, 0.0, 5.14)
			self.scale = 0.002 # 1/500th - this will scale up as it moves to it's destination...
			self.color = (0.0, 1.0, 0.0, 0.5)
		else:
			self.pos = self.dest
			if landscape:
				# scale so that we're smaller closer to center
				maxdist = 1.1 # based on the current body model
				maxscale = 0.5
				dist = math.sqrt(dest[0]*dest[0] + dest[1]*dest[1])			
				self.color = (1.0, 0.0, 0.0, 0.5)
				# two points (maxdist, maxscale), (0, .002)
				slope = (maxscale - .002)/maxdist
				#sub known vars
				#1.0 = slope*maxdist + b
				# solve for b
				b = maxscale - slope*maxdist
				# for a given x
				self.scale = slope*dist + b
			else:
				self.scale = 1.0

	def draw(self):
		glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.color)
		#glMaterialfv(GL_FRONT, GL_SHININESS, [1.0, 1.0, 1.0, 1.0])
		#glColor3f(self.color[0],self.color[1],self.color[2])
		glPushMatrix()
		glTranslatef(*self.pos)
		glScalef(self.scale, self.scale, self.scale)
		glRotatef(self.angle, *self.rotvec)
		glBegin(GL_POLYGON)
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
