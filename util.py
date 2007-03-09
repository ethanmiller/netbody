import math

class CONST:
	SAVE_FRAMES = False
	# general visualization constants
	VIZSIZE = (800, 450)	
	BGCOLOR = (0.9, 0.9, 0.85, 0.0)
	CENTER = (50.0, 50.0, 23.0)
	ROTATE_RATE = 0.025
	PROXIMITY_RANGE = (-60, -20)
	PANEL_WIDTH = 128
	PANEL_PADDING = 5
	# data collection const - these pased on the yahoo pipes feed I created...
	FEED_URL = 'http://pipes.yahoo.com/pipes/eBEyVbXK2xGId7CoE2_cUw/run?_render=json'
	TITLE_FLICKR_RECENT = 'flickr_recent'
	TITLE_NEWS_TOP = 'news_top'
	TITLE_NEWS_PHOTOS = 'news_photos'
	# image/text object constants
	BIT_DRIFT_LIMIT = 10 # [[[testing value]]]
	#BIT_DRIFT_LIMIT = 120 
	BIT_TRAJ_VEC_RANGE = (-0.05, 0.05) # [[[testing value]]]
	#BIT_TRAJ_VEC_RANGE = (-0.01, 0.01)
	BIT_STUCK_LIMIT = 50000
	BIT_UNSTUCK_ALPHA = 0.2
	BIT_ROT_INC_RANGE = (1.0, 2.0)
	# "attention" block constants
	ATT_ANI_STEPS = 16.0
	ATT_POS_INDX_START = 4950
	ATTCOLOR = (1.0, 0.0, 0.0)

def distance(pta, ptb):
	diff = [x[1] - x[0] for x in zip(pta, ptb)]
	return math.sqrt(reduce(lambda x, y: x+y, [z*z for z in diff]))

def pow2(n):
	n = n -1
	n = n | (n >> 1)
	n = n | (n >> 2)
	n = n | (n >> 4)
	n = n | (n >> 8)
	n = n | (n >> 16)
	n = n | (n >> 32)
	n = n + 1
	return n
