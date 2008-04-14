from entities import *
entity_list = {}
next_seed = None
pnetwork = None

def spider():
	global entity_list, next_seed, pnetwork
	if not next_seed: 
		if len(entity_list.keys()) > 0 : raise RuntimeError, "spider without argument only to initialize"
		entity = Tag(tag='identity')
		entity.is_seed = True
		entity.index = 0
		entity_list[str(entity.__class__)] = [entity]
		base.posi.add_node(str(entity.__class__))
	else:
		entity = next_seed
		entity.is_seed = True
		entity.next_seed = False
	entity.active = True
	print '\n\n__main spider() call on entity id=%s [%s]__ %s' % (entity.id, entity.__class__, datetime.datetime.today().strftime("%a %I:%M%p"))
	network = entity.spider() 
	ncount = len(network)
	if ncount == 0 or not entity.spiderable:
		print "~~found 0 other entities, or nonspiderable entity. Reverting to last set"
		network = pnetwork # reuse the last set and hope we get unstuck
		ncount = len(network)
	else:
		pnetwork = network # save this network in case we need to come back to it
	rchoice = random.randrange(len(network))
	addcount = 0
	for i, e in enumerate(network):
		added, e = get_or_add(e)
		if added: addcount += 1
		# this flag lets entity know to animate
		e.active = True
		# make sure spidering entity has all the connections
		entity.add_connection(str(e.__class__), e.index)
		e.del_connection(str(entity.__class__), entity.index)
		if rchoice == i : 
			next_seed = e # choose a seed for next spider
			e.next_seed = True
			print "seed id = %s [%s]" % (e.id, e.__class__)
	util.log('START_SPIDER')
	print "++ %s entities, and %s of those were new ++" % (ncount, addcount)

def get_or_add(entity):
	"""if the entity is in the collection already, return the collected one. Otherwise add it to collection
	returns boolean added, and obj"""
	ekey = str(entity.__class__)
	if entity_list.has_key(ekey):
		for e in entity_list[ekey]:
			if e.matches(entity): return False, e
		entity.approve()
		entity.index = len(entity_list[ekey])
		entity_list[ekey].append(entity)
		base.posi.add_node(str(entity.__class__))
		return True, entity
	else:
		# first of its type
		entity.approve()
		entity.index = 0
		entity_list[ekey] = [entity]
		base.posi.add_node(str(entity.__class__))
		return True, entity
