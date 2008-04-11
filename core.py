import random, util
from vec2d import vec2d

class Position:
	def __init__(self, x, y, type, indx):
		# the x position of each entity is relative to the colx so that I can push over the whole column
		self.x = x
		self.y = y
		self.colx = 0 # this should get set
		self.w = util.CONST.ENTITY_DEFAULT_SIZE
		self.h = util.CONST.ENTITY_DEFAULT_SIZE
		self.ctype = type
		self.indx = indx

	def with_offset(self, cx):
		self.colx = cx
		return self

	def xy(self):
		return (self.colx + self.x, self.y)

class Positioner:
	def __init__(self):
		""" This class keeps track of entity positions and dimensions 
			It will determine position in relation to other positions and dimensions 
			But entities have to update this class with their dimensions
		"""
		self.positions_meta = {} # {'class_name' : {'colx' : 0, 'ct' : 0, 'last_pos' : (1, 1)}, ...}
		self.positions = [] # containing : {'class_name' : {'colx' : 0, 'entity_pos' : [(x,y,w,h), (x,y,w,h), ...]}, ... }
		self.total_width = 0

	def add_node(self, type):
		if not self.positions_meta.has_key(type):
			nx = self.total_width + util.CONST.GRID_SPACE
			self.positions_meta[type] = {'colx' : nx, 'ct' : 0, 'last_pos' : (0, util.CONST.GRID_SPACE)}
			self.positions.append(Position(0, util.CONST.GRID_SPACE, type, 0))
			self.total_width = self.total_width + util.CONST.GRID_SPACE
		else:
			# last entity_pos gives ypos
			nx, ny = self.positions_meta[type]['last_pos']
			ny = ny + util.CONST.GRID_SPACE
			if ny >= util.CONST.WIN_HEIGHT:
				# we have to bump the other columns to the right
				for e in self.positions_meta.values():
					if e['colx'] > self.positions_meta[type]['colx']: e['colx'] = e['colx'] + util.CONST.GRID_SPACE
				# bump this one
				self.positions_meta[type]['colx'] = self.positions_meta[type]['colx'] + util.CONST.GRID_SPACE
				nx = nx + util.CONST.GRID_SPACE
				ny = util.CONST.GRID_SPACE
			ni = self.positions_meta[type]['ct'] + 1
			self.positions.append(Position(nx, ny, type, ni))
			# update meta values
			self.positions_meta[type]['ct'] = ni
			self.positions_meta[type]['last_pos'] = (nx, ny)

	def update_size(self, type, index, w, h):
		p = self.get_pos(type, index)
		p.w = w
		p.h = h

	def get_pos(self, type, index):
		for p in [x for x in self.positions if x.ctype == type]:
			if p.indx == index: return p.with_offset(self.positions_meta[type]['colx'])
		return None

class Curve:
	""" A curve owned by an entity to connect it to another entity """
	def __init__(self, otype, oindx):
		self.end_type = otype
		self.end_indx = oindx
		self.control_pts = []
		self.control_xoff = (random.randint(util.CONST.CURVE_X_VAR_MIN, util.CONST.CURVE_X_VAR_MAX), random.randint(util.CONST.CURVE_X_VAR_MIN, util.CONST.CURVE_X_VAR_MAX))
		self.segments = random.randint(util.CONST.CURVE_SEG_MIN, util.CONST.CURVE_SEG_MAX)
		self.curve_pts = []
		self.curve_indx = 0
		self.last_oxy = (0, 0)

	def matches(self, t, i):
		return self.end_type == t and self.end_indx == i

	def calc_ctrl_pts(self, x, y):
		opos = posi.get_pos(self.end_type, self.end_indx)
		ox, oy = opos.xy()
		# randomize the horizontal change, leave the vertical aligned
		x1 = max(x, ox) + self.control_xoff[0]
		y1 = y
		x2 = max(x, ox) + self.control_xoff[1]
		y2 = oy
		self.control_pts = [vec2d(x, y), vec2d(x1, y1), vec2d(x2, y2), vec2d(ox, oy)]

	def set_ctrl_pts(self, x, y, that_xy_changed):
		opos = posi.get_pos(self.end_type, self.end_indx)
		oxy = opos.xy()
		this_xy_changed = oxy != self.last_oxy
		self.last_oxy = oxy
		if not self.control_pts or that_xy_changed or this_xy_changed:
			self.calc_ctrl_pts(x, y)

	def set_curve_pts(self, that_xy_changed):
		if not self.control_pts: raise RuntimeError, "Have to set control points before calculating curve points"
		opos = posi.get_pos(self.end_type, self.end_indx)
		oxy = opos.xy()
		this_xy_changed = oxy != self.last_oxy
		self.last_oxy = oxy
		if not self.curve_pts or that_xy_changed or this_xy_changed:
			self.curve_pts = util.calculate_bezier(self.control_pts, self.segments)

	def draw(self, ctx, isactive):
		# draw out as much of the curve as we have at this point
		ret_curve_done = True
		if isactive:
			# draw segment by segment
			if self.curve_indx < len(self.curve_pts): 
				self.curve_indx = self.curve_indx + 1
				ret_curve_done = False
			ctx.move_to(self.curve_pts[0][0], self.curve_pts[0][1])
			for i, p in enumerate(self.curve_pts[:self.curve_indx]):
				if i == 0 : continue
				ctx.line_to(p[0], p[1])
		else:
			# just draw the curve
			ctx.move_to(self.control_pts[0][0], self.control_pts[0][1])
			ctx.curve_to(self.control_pts[1][0], self.control_pts[1][1], 
						self.control_pts[2][0], self.control_pts[2][1],
						self.control_pts[3][0], self.control_pts[3][1])
		ctx.stroke()
		# need to advise endpoint entity when curve is done
		return ret_curve_done

class Entity:
	""" Base class for all entities in netbody visualization """
	def __init__(self, kwarg_keys, **kwargs):
		chkwargs = kwarg_keys[:]
		for k,v in kwargs.iteritems():
			if k not in chkwargs: raise TypeError, "Unexpected arg :: %s" % k
			indxof = chkwargs.index(k)
			del(chkwargs[indxof])
			setattr(self, k, v)
		if chkwargs: raise TypeError, "Missing arg(s) :: %s" % chkwargs
		self.last_xy = (0, 0)
		self.active = False
		self.is_seed = False
		self.width = util.CONST.ENTITY_DEFAULT_SIZE
		self.ext_width = util.CONST.ENTITY_DEFAULT_SIZE
		self.height = util.CONST.ENTITY_DEFAULT_SIZE
		self.ext_height = util.CONST.ENTITY_DEFAULT_SIZE
		self.spiderable = True
		self.curves = []

	def has_curve(self, type, indx):
		for c in self.curves:
			if c.matches(type, indx): return True
		return False
	
	def add_connection(self, type, indx):
		if not self.has_curve(type, indx):
			self.curves.append(Curve(type, indx))

	def del_connection(self, type, indx):
		for i, c in enumerate(self.curves):
			if c.matches(type, indx): del(self.curves[i]); return

	def approve(self):
		"""any expensive opperations go here instead of __init__"""
		pass

	def spider(self):
		"""spider is always overidden"""
		raise RuntimeError, "Must override base Entity spider()"

	def matches(self, other):
		"""the base match checking"""
		return self.id == other.id


	def draw_network(self, ctx):
		# have we moved?
		pos = posi.get_pos(str(self.__class__), self.index)
		xy = pos.xy()
		has_changed = xy != self.last_xy
		self.last_xy = xy
		curves_done = True
		for curve in self.curves:
			curve.set_ctrl_pts(xy[0], xy[0], has_changed)
			curve.set_curve_pts(has_changed)
			if not curve.draw(ctx, self.active): curves_done = False
		if curves_done:
			self.active = False
			self.is_seed = False		

	def grow_box(self):
		growing = False
		if self.width < self.ext_width:
			growing = True
			wdiff = self.ext_width - self.width
			self.width = self.width + wdiff*util.CONST.GROW_BOX_N
			if abs(wdiff) < 0.005:
				self.width = self.ext_width
		if self.height < self.ext_height:
			growing = True
			hdiff = self.ext_height - self.height
			self.height = self.height + hdiff*util.CONST.GROW_BOX_N
			if abs(hdiff) < 0.005:
				self.height = self.ext_height
		return growing

	def draw(self, ctx):
		xy = self.last_xy # we can use last_xy here because it was set during draw_network()
		if self.is_seed : ctx.set_source_rgb(1.0, 0.2, 0.2)
		else : ctx.set_source_rgb(0.2, 0.2, 0.2)
		if self.active:
			# if we're not up to extended size, grow
			still_growing = self.grow_box()
		ctx.rectangle(xy[0], xy[1], self.width, self.height)
		#ctx.close_path()
		ctx.fill()



################ the positioner class
posi = Positioner()
