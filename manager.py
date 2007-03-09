import infobj, collector, panel, util

class Manager:
	def __init__(self):
		self.net = collector.Collector()
		self.panel = panel.Panel()
		self.paneldat = []
		self.bits = []
		self.attention = infobj.Attention()
	
	def draw(self, mode):	
		if mode == 2:
			# 2d rendering - this always happens after 3d rendering
			# and so self.paneldat contains data from that previous rendering
			self.panel.draw(self.paneldat, self.attention.screenpos)
		elif mode == 3:
			self.draw3d()

	def draw3d(self):
		attention_at = self.attention.draw()
		for d in self.net.data():
			self.bits.append(infobj.Bit(d))
		self.paneldat = [] # clear out paneldat to repopulate
		kill_list = [] # bits that have floated too far away
		sort_up_list = [] # bits that are now opaque, and should be drawn first
		past_unstuck = False # start collecting stuck bits for resorting only after we've past some unstuck ones
		for i, b in enumerate(self.bits):
			b.draw(attention_at)
			dist = util.distance(util.CONST.CENTER, b.pos)
			if dist > util.CONST.BIT_DRIFT_LIMIT:
				kill_list.append(i)
			if not b.stuck and not past_unstuck:
				past_unstuck = True
			if b.stuck:
				self.paneldat.append(b.netdat)
				if past_unstuck:
					sort_up_list.append(i)
				
		for k in kill_list:
			del(self.bits[k])
		for s in sort_up_list:
			try:
				popped = self.bits.pop(s)
				self.bits.insert(0, popped)
			except IndexError:
				pass # that bit must've got killed..
		
