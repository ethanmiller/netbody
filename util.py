import math, Image

class CONST:
	SAVE_FRAMES = False
	SERVICE_HIT_PAUSE = 5 # how many seconds to pause between hitting apis/feeds
	WIN_WIDTH = 20
	WIN_HEIGHT = 20
	

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
