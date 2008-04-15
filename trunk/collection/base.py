import random, util, manager, math
from vec2d import vec2d

class Position:
	def __init__(self, x, y, type, indx):
		# the x position of each entity is relative to the colx so that I can push over the whole column
		self.x = x
		self.homex = x
		self.y = y
		self.homey = y
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

	def wh(self):
		return (self.w, self.h)

	def drift_home(self):
		hithomex = False
		hithomey = False
		if self.x != self.homex:
			xdiff = self.homex - self.x 
			self.x = self.x + xdiff*util.CONST.DRIFT_HOME_N 
			if abs(xdiff) < 0.005:
				self.x = self.homex
				hithomex = True
		if self.y != self.homey:
			ydiff = self.homey - self.y 
			self.y = self.y + ydiff*util.CONST.DRIFT_HOME_N
			if abs(ydiff) < 0.005:
				self.y = self.homey
				hithomey = True
		if hithomey and hithomex: 
			util.log('ENT_HIT_HOME')

class Positioner:
	def __init__(self):
		""" This class keeps track of entity positions and dimensions 
			It will determine position in relation to other positions and dimensions 
			But entities have to update this class with their dimensions
		"""
		self.positions_meta = {} # {'class_name' : {'colx' : 0, 'colx_targ' : 0, 'ct' : 0, 'last_pos' : (1, 1)}, ...}
		self.positions = [] 
		self.total_width = 0

	def add_node(self, type):
		if not self.positions_meta.has_key(type):
			nx = self.total_width + util.CONST.GRID_SPACE
			self.positions_meta[type] = {'colx' : nx, 'colx_targ' : nx, 'ct' : 0, 'last_pos' : (0, util.CONST.GRID_SPACE)}
			self.positions.append(Position(0, util.CONST.GRID_SPACE, type, 0))
			self.total_width = self.total_width + util.CONST.GRID_SPACE
		else:
			# last entity_pos gives ypos
			nx, ny = self.positions_meta[type]['last_pos']
			ny = ny + util.CONST.GRID_SPACE
			if ny >= util.CONST.WIN_HEIGHT/2:
				# we have to bump the other columns to the right
				for e in self.positions_meta.values():
					if e['colx'] > self.positions_meta[type]['colx']: e['colx_targ'] = e['colx'] + util.CONST.GRID_SPACE
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

	def force_place(self):
		pad = util.CONST.BOX_ARROW_OFFSET*2 
		for i, pos in enumerate(self.positions):
			for pos2 in self.positions[i+1:]:
				has_minimized = False
				if pos.w == util.CONST.ENTITY_DEFAULT_SIZE and pos.h == util.CONST.ENTITY_DEFAULT_SIZE:
					has_minimized = True
					pos.drift_home()
				if pos2.w == util.CONST.ENTITY_DEFAULT_SIZE and pos2.h == util.CONST.ENTITY_DEFAULT_SIZE:
					has_minimized = True
					pos2.drift_home()
				if has_minimized: continue
				posx, posy = pos.xy() # use this to get abs x position
				pos2x, pos2y = pos2.xy()
				if posy + pos.h + pad < pos2y: continue # bottom of pos above top of pos2
				if posy > pos2y + pos2.h + pad: continue # top of pos below bottom of pos2
				if posx + pos.w + pad < pos2x: continue # right of pos to the left of left side of pos2
				if posx > pos2x + pos2.w + pad: continue # left of pos to the right of right side of pos2
				mid = (posx + pos.w/2, posy + pos.h/2)
				mid2 = (pos2x + pos2.w/2, pos2y + pos2.h/2)
				xdiff, ydiff = (mid2[0] - mid[0], mid2[1] - mid[1])
				dist = math.sqrt(xdiff*xdiff + ydiff*ydiff)
				pushx = xdiff*util.CONST.NO_OVERLAP_FORCE
				pushy = ydiff*util.CONST.NO_OVERLAP_FORCE

				pos2.x = pos2.x + pushx
				pos.x = pos.x - pushx
				# update actual pos vars
				pos2x = pos2x + pushx
				posx = posx - pushx
				# make sure we're not off the vizualization
				if pos2x + pos2.w >= util.CONST.WIN_WIDTH or pos2x <= 0:
					# push both the other way
					pos2.x = pos2.x - pushx*2
					pos.x = pos.x - pushx
				if posx + pos.w >= util.CONST.WIN_WIDTH or posx <= 0:
					# push both the other way
					pos.x = pos.x + pushx*2
					pos2.x + pushx
				pos2.y = pos2.y + pushy
				pos.y = pos.y - pushy
				# update actual pos - not strictly necessary, but for consistency
				pos2y = pos2y + pushy
				posy = posy - pushy
				# make sure we're not pushed off the page
				if pos2y + pos2.h >= util.CONST.WIN_HEIGHT or pos2y <= 0:
					# push
					pos2.y = pos2.y - pushy*2
					pos.y = pos.y - pushy
				if posy + pos.h >= util.CONST.WIN_HEIGHT or posy <= 0:
					# push
					pos.y = pos.y + pushy*2
					pos2.y = pos2.y + pushy
		self.drift_col()

	def drift_col(self):
		for e in self.positions_meta.values():
			if e['colx'] != e['colx_targ']:
				coldiff = e['colx_targ'] - e['colx']
				e['colx'] = e['colx'] + coldiff*util.CONST.COL_DRIFT_N
				if abs(coldiff) < 0.005:
					e['colx'] = e['colx_targ']

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
		self.last_owh = (0, 0)
		self.last_xy = (0, 0)
		self.last_wh = (0, 0)
		self.recalc = False

	def matches(self, t, i):
		return self.end_type == t and self.end_indx == i

	def calc_ctrl_pts(self, from_xy, from_wh, to_xy, to_wh):
		x, y = from_xy
		x = x + from_wh[0]
		ox, oy = to_xy
		ox = ox + to_wh[0]
		if from_wh[1] > util.CONST.ENTITY_DEFAULT_SIZE:
			x = x + util.CONST.BOX_ARROW_OFFSET
			y = y + from_wh[1]/2
		if to_wh[1] > util.CONST.ENTITY_DEFAULT_SIZE:
			ox = ox + util.CONST.BOX_ARROW_OFFSET
			oy = oy + to_wh[1]/2
		# randomize the horizontal change, leave the vertical aligned
		x1 = max(x, ox) + self.control_xoff[0]
		y1 = y
		x2 = max(x, ox) + self.control_xoff[1]
		y2 = oy
		self.control_pts = [vec2d(x, y), vec2d(x1, y1), vec2d(x2, y2), vec2d(ox, oy)]

	def set_ctrl_pts(self, pos):
		opos = posi.get_pos(self.end_type, self.end_indx)
		oxy = opos.xy()
		owh = opos.wh()
		xy = pos.xy()
		wh = pos.wh()
		this_xy_changed = oxy != self.last_oxy or owh != self.last_owh
		that_xy_changed = xy != self.last_xy or wh != self.last_wh
		self.recalc = this_xy_changed or that_xy_changed
		self.last_oxy = oxy
		self.last_xy = xy
		if not self.control_pts or self.recalc:
			self.calc_ctrl_pts(xy, wh, oxy, owh)

	def set_curve_pts(self):
		if not self.control_pts: raise RuntimeError, "Have to set control points before calculating curve points"
		if not self.curve_pts or self.recalc:
			self.curve_pts = util.calculate_bezier(self.control_pts, self.segments)
			self.recalc = False

	def draw(self, ctx, isactive, isseed):
		# draw out as much of the curve as we have at this point
		ret_curve_done = True
		if isseed:
			red = util.mapval(self.curve_indx, 0, len(self.curve_pts), 1.0, 0.7)
			gb = util.mapval(self.curve_indx, 0, len(self.curve_pts), 0.2, 0.7)
			alpha = util.mapval(self.curve_indx, 0, len(self.curve_pts), 1.0, 0.5)
			ctx.set_source_rgba(red, gb, gb, alpha)
			# draw segment by segment
			if self.curve_indx < len(self.curve_pts): 
				self.curve_indx = self.curve_indx + 1
				ret_curve_done = False
			ctx.move_to(self.curve_pts[0][0], self.curve_pts[0][1])
			for i, p in enumerate(self.curve_pts[:self.curve_indx]):
				if i == 0 : continue
				ctx.line_to(p[0], p[1])
		else:
			ctx.set_source_rgba(0.7, 0.7, 0.7, 0.5)
			# just draw the curve
			ctx.move_to(self.control_pts[0][0], self.control_pts[0][1])
			ctx.curve_to(self.control_pts[1][0], self.control_pts[1][1], 
						self.control_pts[2][0], self.control_pts[2][1],
						self.control_pts[3][0], self.control_pts[3][1])
		ctx.stroke()
		if ret_curve_done : manager.entity_list[self.end_type][self.end_indx].curve_to_finished = True
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
		self.last_pos = None
		self.active = False
		self.is_seed = False
		self.next_seed = False
		self.width = util.CONST.ENTITY_DEFAULT_SIZE
		self.ext_width = util.CONST.ENTITY_DEFAULT_SIZE
		self.height = util.CONST.ENTITY_DEFAULT_SIZE
		self.ext_height = util.CONST.ENTITY_DEFAULT_SIZE
		self.extent_set = False
		self.spiderable = True
		self.curves = []
		self.curve_to_finished = False
		self.curve_to_finished_last = False
		self.grow_box_n = random.uniform(util.CONST.GROW_BOX_VAR_MIN, util.CONST.GROW_BOX_VAR_MAX)
		self.r = 0.2
		self.gb = 0.2

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

	def shrink_box(self):
		if self.width > util.CONST.ENTITY_DEFAULT_SIZE:
			wdiff = self.width - util.CONST.ENTITY_DEFAULT_SIZE
			self.width = self.width - wdiff*util.CONST.SHRINK_BOX_N
			if abs(wdiff) < 0.005:
				self.width = util.CONST.ENTITY_DEFAULT_SIZE
		if self.height > util.CONST.ENTITY_DEFAULT_SIZE:
			hdiff = self.height - util.CONST.ENTITY_DEFAULT_SIZE
			self.height = self.height - hdiff*util.CONST.SHRINK_BOX_N
			if abs(hdiff) < 0.005:
				self.height = util.CONST.ENTITY_DEFAULT_SIZE

	def grow_box(self):
		growing = False
		if self.width < self.ext_width:
			growing = True
			wdiff = self.ext_width - self.width
			self.width = self.width + wdiff*self.grow_box_n
			if abs(wdiff) < 0.005:
				self.width = self.ext_width
		if self.height < self.ext_height:
			growing = True
			hdiff = self.ext_height - self.height
			self.height = self.height + hdiff*self.grow_box_n
			if abs(hdiff) < 0.005:
				self.height = self.ext_height
		return growing

	def draw_network(self, ctx):
		pos = posi.get_pos(str(self.__class__), self.index)
		self.last_pos = pos
		curves_done = True
		for curve in self.curves:
			curve.set_ctrl_pts(pos)
			curve.set_curve_pts()
			if not curve.draw(ctx, self.active, self.is_seed): curves_done = False
		if curves_done and self.is_seed:
			self.is_seed = False
			self.active = False
			util.log('ENT_FINISH_SPIDER')

	def set_col(self, ctx):
		targ = 0.2
		alpha = 0.8
		if self.is_seed : 
			targ = 0.8
		elif self.next_seed : 
			targ = 0.6
		if hasattr(self, 'status'):
			if self.status != 200:
				targ = 0.4
				alpha = 0.4
		if self.r != targ:
			coldiff = targ - self.r 
			self.r = self.r + coldiff*util.CONST.COLOR_DRIFT_N
			if abs(coldiff) < 0.005:
				self.r = targ
		ctx.set_source_rgba(self.r, self.gb, self.gb, alpha)

	def draw(self, ctx):
		xy = self.last_pos.xy() # we can use last_pos here because it was set during draw_network()
		self.set_col(ctx)
		if self.active:
			# if we're not up to extended size, grow
			still_growing = self.grow_box()
			if not still_growing and self.curve_to_finished and not self.is_seed and not self.next_seed:
				self.active = False
				self.curve_to_finished = False # reset this in case we get curved to again...
		else:
			self.shrink_box()
		ctx.rectangle(xy[0], xy[1], self.width, self.height)
		ctx.fill()
		if self.height > util.CONST.ENTITY_DEFAULT_SIZE:
			# draw a little triangle on the right side
			ctx.move_to(xy[0] + self.width, xy[1])
			ctx.line_to(xy[0] + self.width + util.CONST.BOX_ARROW_OFFSET, xy[1] + self.height/2)
			ctx.line_to(xy[0] + self.width, xy[1] + self.height)
			ctx.close_path()
			ctx.fill()
		# update posi about my position
		posi.update_size(str(self.__class__), self.index, self.width, self.height)
		if self.curve_to_finished != self.curve_to_finished_last and self.curve_to_finished:
			util.log('ENT_CURVE_GOT_ME')
		self.curve_to_finished_last = self.curve_to_finished


################ the positioner class
posi = Positioner()
