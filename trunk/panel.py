from OpenGL.GL import *
import util

class Panel:
	def __init__(self):
		pass

	def draw(self, dat, atat):
		#at = self.screen_att(atat)
		glColor4f(0.4, 0.4, 1.0, 1.0)
		glBegin(GL_QUADS)
		glVertex2f(10.0, 10.0)
		glVertex2f(200.0, 10.0)
		glVertex2f(200.0, 200.0)
		glVertex2f(10.0, 200.0)
		glEnd()

		at_xdiff = atat[0] - 200.0
		glBegin(GL_LINE_STRIP)
		glVertex3f(200.0, 200.0, 0.0)
		glVertex3f(at_xdiff/2.0 + 200.0, 200.0, 0.0)
		glVertex3f(at_xdiff/2.0 + 200.0, atat[1], 0.0)
		glVertex3f(*atat)
		glEnd()

