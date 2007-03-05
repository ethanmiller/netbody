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
		for i, b in enumerate(self.bits):
			b.draw(attention_at)
			dist = util.distance(util.CONST.CENTER, b.pos)
			if dist > util.CONST.BIT_DRIFT_LIMIT:
				kill_list.append(i)
		for k in kill_list:
			del(self.bits[k])
		
