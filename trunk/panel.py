from OpenGL.GL import *
import util

class Panel:
	def __init__(self):
		pass

	def draw(self, dat, atat):
		#at = self.screen_att(atat)
		glColor4f(0.6, 0.6, 0.55, 1.0)
		glBegin(GL_QUADS)
		glVertex2f(util.CONST.PANEL_PADDING, util.CONST.PANEL_PADDING)
		glVertex2f(util.CONST.PANEL_WIDTH, util.CONST.PANEL_PADDING)
		glVertex2f(util.CONST.PANEL_WIDTH, util.CONST.VIZSIZE[1] - util.CONST.PANEL_PADDING * 2)
		glVertex2f(util.CONST.PANEL_PADDING,  util.CONST.VIZSIZE[1] - util.CONST.PANEL_PADDING * 2)
		glEnd()

		at_xdiff = atat[0] - util.CONST.PANEL_WIDTH
		glBegin(GL_LINE_STRIP)
		glVertex3f(util.CONST.PANEL_WIDTH, 430.0, 0.0)
		glVertex3f(at_xdiff/2.0 + util.CONST.PANEL_WIDTH, 430.0, 0.0)
		glVertex3f(at_xdiff/2.0 + util.CONST.PANEL_WIDTH, atat[1], 0.0)
		glVertex3f(*atat)
		glEnd()

