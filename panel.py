from OpenGL.GL import *
import util, time, Image, ImageDraw, ImageFont

class Panel:
	def __init__(self):
		self.font = ImageFont.truetype('resources/NewMedia.ttf', 12)
		self.time_tex = 0

	def draw(self, dat, atat):
		#at = self.screen_att(atat)
		glColor4f(0.6, 0.6, 0.55, 1.0)
		glBegin(GL_QUADS)
		glVertex2f(util.CONST.PANEL_PADDING, util.CONST.PANEL_PADDING)
		glVertex2f(util.CONST.PANEL_WIDTH + util.CONST.PANEL_PADDING, util.CONST.PANEL_PADDING)
		glVertex2f(util.CONST.PANEL_WIDTH + util.CONST.PANEL_PADDING, util.CONST.VIZSIZE[1] - util.CONST.PANEL_PADDING * 2)
		glVertex2f(util.CONST.PANEL_PADDING,  util.CONST.VIZSIZE[1] - util.CONST.PANEL_PADDING * 2)
		glEnd()

		at_xdiff = atat[0] - util.CONST.PANEL_WIDTH
		glBegin(GL_LINE_STRIP)
		glVertex3f(util.CONST.PANEL_WIDTH, 430.0, 0.0)
		glVertex3f(at_xdiff/2.0 + util.CONST.PANEL_WIDTH, 430.0, 0.0)
		glVertex3f(at_xdiff/2.0 + util.CONST.PANEL_WIDTH, atat[1], 0.0)
		glVertex3f(*atat)
		glEnd()

		stime = time.strftime('%a, %b %d %H:%M:%S')
		im = Image.new('RGB', (128, 32), (255, 255, 255))
		drawr = ImageDraw.Draw(im)
		drawr.text((5, 15), stime, font=self.font, fill=0)

		glBindTexture(GL_TEXTURE_2D, self.time_tex)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.size[0], im.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, im.tostring())
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0); glVertex3f(5.0, 408.0, 0.0)
		glTexCoord2f(1.0, 0.0); glVertex3f(133.0, 408.0, 0.0)
		glTexCoord2f(1.0, 1.0); glVertex3f(133.0, 440.0, 0.0)
		glTexCoord2f(0.0, 1.0); glVertex3f(5, 440.0, 0.0)
		glEnd()

