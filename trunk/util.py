import math, Image

class CONST:
	SAVE_FRAMES = True
	# ---------- general visualization constants
	VIZSIZE = (800, 450)	
	BGCOLOR = (0.9, 0.9, 0.85, 0.0)
	CENTER = (50.0, 50.0, 23.0)
	ROTATE_RATE = 0.025
	PROXIMITY_RANGE = (-60, -20)
	FRAME_PAUSE = 0.001
	IPANEL_WIDTH = 50
	IPANEL_PADDING = 5
	WPANEL_HEIGHT = 25
	WPANEL_PADDING = 5
	PANEL_BG = (219, 219, 208, 1.0)
	WORD_PADDING = 5.0
	# ---------- data collection const - these pased on the yahoo pipes feed I created...
	FEED_URL = 'http://pipes.yahoo.com/pipes/eBEyVbXK2xGId7CoE2_cUw/run?_render=json'
	FEED_TIMEOUT = 20.0
	TITLE_FLICKR_RECENT = 'flickr_recent'
	TITLE_NEWS_TOP = 'news_top'
	TITLE_NEWS_PHOTOS = 'news_photos'
	DB_LOC = 'resources/netbodydb'
	COLLECTION_PAUSE = 180 # in seconds
	IMG_PER_FRAME_RANGE = (0, 3)
	IMG_TIMEOUT = 8.0
	# ---------- image/text object constants
	BIT_DRIFT_LIMIT = 55
	BIT_SPEED_RANGE = (-0.004, 0.004)
	BIT_STUCK_LIMIT = 50000
	BIT_UNSTUCK_ALPHA = 0.2
	BIT_ROT_INC_RANGE = (1.0, 2.0)
	THUMBSIZE = (50, 50)
	# ---------- "attention" block constants
	ATT_ANI_STEPS = 16.0
	ATT_POS_INDX_START = 4650
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

def sizeimg(im):
	if im.size[0] >= im.size[1]:
		im.thumbnail(CONST.THUMBSIZE, Image.ANTIALIAS)
		return im
	else:
		fac = (CONST.THUMBSIZE[0]*1.0)/im.size[0]
		ysize = int((im.size[1]*1.0)*fac)
		return im.resize((CONST.THUMBSIZE[0], ysize), Image.ANTIALIAS)

def log(msg):
	if msg == 'INIT':
		f = open('resources/score.txt', 'w')
		f.write('')
		f.close()
		return
	f = open('resources/score.txt', 'a')
	if msg == 'ENDFRAME':
		f.write('\n')
		f.close()
		return
	f.write("%s|" % msg)
	f.close()
	
