import random

class Collector:
	def __init__(self):
		pass
	
	def data(self):
		return [x for x in range(random.randint(0, 6))]
