import math, Image

class CONST:
	SAVE_FRAMES = False
	SERVICE_HIT_PAUSE = 10 # how many seconds to pause between hitting apis/feeds
	WIN_WIDTH = 20
	WIN_HEIGHT = 20
	NOISE_WORDS = "about,after,all,also,an,and,another,any,are,as,at,be,because,been,before,being,between,both,but,by,came,can,come,could,did,do,each,for,from,get,got,has,had,he,have,her,here,him,himself,his,how,if,in,into,is,it,like,make,many,me,might,more,most,much,must,my,never,now,of,on,only,or,other,our,out,over,said,same,see,should,since,some,still,such,take,than,that,the,their,them,then,there,these,they,this,those,through,to,too,under,up,very,was,way,we,well,were,what,where,which,while,who,with,would,you,your,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,$,1,2,3,4,5,6,7,8,9,0,_".split(",")

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
	elapsed = time.clock() - mark
	if elapsed < CONST.SERVICE_HIT_PAUSE:
		sleeptime = CONST.SERVICE_HIT_PAUSE - elapsed
		print ".... pausing %s seconds for %s ...." % (sleeptime, for_whom)
		time.sleep(sleeptime)
	return time.clock()

def unicode_enforce(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj
