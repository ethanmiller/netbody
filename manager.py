import math
import infobj, collector

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
		kill_list = []
		for i, b in enumerate(self.bits):
			b.draw(attention_at)
			diff = [50.0-b.pos[0], 50.0-b.pos[1], 23.0-b.pos[2]] #from center of figure
			dist = math.sqrt(reduce(lambda x, y: x+y, [v*v for v in diff]))
			if dist > 60:
				kill_list.append(i)
		if kill_list:
			for k in kill_list:
				del(self.bits[k])
		
