import infobj, collector, util

class Manager:
	def __init__(self):
		self.net = collector.Collector()
		self.bits = []
		self.attention = infobj.Attention()
	
	def draw(self, dat):	
		# dat = a list of image resources??
		attention_at = self.attention.draw()
		for d in dat:
			self.bits.append(infobj.Bit(d))
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
			if b.stuck and past_unstuck:
				sort_up_list.append(i)
				
		for k in kill_list:
			del(self.bits[k])
		for s in sort_up_list:
			try:
				popped = self.bits.pop(s)
				self.bits.insert(0, popped)
			except IndexError:
				pass # that bit must've got killed..
		
