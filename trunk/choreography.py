import body

class Manager:
	def __init__(self):
		self.frames = 500 # how many frames one cycle should last
		self.breakpoint = 450 # the breakpoint determines the time for the switch
		self.counter = 0
		self.scaled = 500.0 # how much bigger large body is
		self.starty = 100 # starting point for body centered in view
		self.zoffset = -35.4 # offset from center of body, to forehead level

		self.desty = self.scaled * self.starty

		self.bodies = [	body.Body(1.0, (self.starty, 0.0), (self.desty, -self.scaled*self.zoffset)), 
				body.Body(self.scaled, (self.starty, self.zoffset), (self.desty, 0.0))]
	
	def draw(self):
		self.bodies[0].draw()
		self.bodies[1].draw()
		if self.counter == self.breakpoint:
			# make inner body outer, 
			self.bodies.reverse()
			
			neworig = (self.starty, self.zoffset)
			newpos = (self.bodies[0].pos[0], self.zoffset)
			newdest = (self.desty, self.zoffset)
			# I dont quite see why setting orig z equal to destintation z works here
			self.bodies[1].set_vars(self.scaled*self.scaled, neworig, newdest, newpos)
		
		if self.counter == self.frames:
			# reset counter, distance, and scale
			self.counter = -1
			self.bodies[0].set_vars(1.0, (self.starty, 0.0), (self.desty, -self.scaled*self.zoffset))
			self.bodies[1].set_vars(self.scaled, (self.starty, self.zoffset), (self.desty, 0.0))
		
		inc = self.timecurve()
		self.bodies[0].pos = self.zcurve(self.bodies[0].init, self.bodies[0].dest, self.bodies[0].ctl, inc)
		self.bodies[1].pos = self.zcurve(self.bodies[1].init, self.bodies[1].dest, self.bodies[1].ctl, inc)

		self.counter += 1
	
	def zcurve(self, start, end, ctl, inc):
		mida = self.midpt(start, ctl, inc)
		midb = self.midpt(ctl, end, inc)
		return self.midpt(mida, midb, inc)

	def midpt(self, start, end, inc):
		return (start[0]+(end[0]-start[0])*inc, start[1]+(end[1]-start[1])*inc)

	def timecurve(self):
		#quintic curve
		t = self.counter * 1.0 / self.frames
		return t*t*t*t*t
