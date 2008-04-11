import math, Image

class CONST:
	SAVE_FRAMES = True
	SERVICE_HIT_PAUSE = 10 # how many seconds to pause between hitting apis/feeds
	WIN_WIDTH = 2560 # we'll scale down to 1280x720
	WIN_HEIGHT = 1440
	NOISE_WORDS = "about,after,all,also,an,and,another,any,are,as,at,be,because,been,before,being,between,both,but,by,came,can,come,could,did,do,each,for,from,get,got,has,had,he,have,her,here,him,himself,his,how,if,in,into,is,it,like,make,many,me,might,more,most,much,must,my,never,now,of,on,only,or,other,our,out,over,said,same,see,should,since,some,still,such,take,than,that,the,their,them,then,there,these,they,this,those,through,to,too,under,up,very,was,way,we,well,were,what,where,which,while,who,with,would,you,your".split(",")
	GRID_SPACE = 30
	CURVE_X_VAR_MIN = 50
	CURVE_X_VAR_MAX = 200
	CURVE_SEG_MIN = 50
	CURVE_SEG_MAX = 200
	ENTITY_DEFAULT_SIZE = 2
	GROW_BOX_N = 0.05

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

def pause(for_whom, mark):
	import time
	elapsed = time.time() - mark
	if elapsed < CONST.SERVICE_HIT_PAUSE:
		sleeptime = CONST.SERVICE_HIT_PAUSE - elapsed
		print ".... pausing %0.2f seconds for %s ...." % (sleeptime, for_whom)
		time.sleep(sleeptime)
	else:
		print ".... no pause for %s ...." % for_whom
	return time.time()

def unicode_enforce(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

def calculate_bezier(p, steps=30):
	"""
	Calculate a bezier curve from 4 control points and return a 
	list of the resulting points.

	The function uses the forward differencing algorithm described here: 
	http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
	"""

	t = 1.0 / steps
	temp = t*t

	f = p[0]
	fd = 3 * (p[1] - p[0]) * t
	fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
	fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t

	fddd = fddd_per_2 + fddd_per_2
	fdd = fdd_per_2 + fdd_per_2
	fddd_per_6 = fddd_per_2 * (1.0 / 3)

	points = []
	for x in range(steps):
		points.append(f)
		f = f + fd + fdd_per_2 + fddd_per_6
		fd = fd + fdd + fddd_per_2
		fdd = fdd + fddd
		fdd_per_2 = fdd_per_2 + fddd_per_2
	points.append(f)
	return points
