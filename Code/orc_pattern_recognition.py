from tree_diff import *

# recognize orc pattern baseed on difference
# between two trees
def orc_pattern_recognition(changes):

	added_children_list = []
	pattern_results = []

	# loop over all the operations
	for i in range(len(changes) - 1, -1, -1):
		op = changes[i]

		# sublayout (or widget) X removed, 
		# or X suddenly added
		# => make X optional
		if (isinstance(op, addNode) \
			or isinstance(op, removeNode)):
			print("888888888")
			print(op.node.widget_id)
			if op.node.widget_id != "Column" and op.node.widget_id != "Row":
				print("Optional Wdiget:", op.node.widget_id)
				pattern_results.append(["Optional Wdiget", op.node.widget_id])
			else:
				added_children_list = op.node.children
					

		# Row change to Column or vice versa 
		# => add Pivot before it
		# sublayout (or widget) X replaced by Y 
		# => Y is alternative for X
		elif isinstance(op, replaceNode):
			 print("Alternative Widget:", op.from_node.widget_id, \
			 				op.to_node.widget_id)
			 pattern_results.append(["Alternative Wdiget", \
			 			op.from_node.widget_id, op.to_node.widget_id])

		# X removed from Row and added to 
		# (possibly new) adjacent Row
		# => merge Rows into HFlow
		# Similar with Columns and HFlow
		# X is moved into different place, 
		# but not just to beginning or end of 
		# adjacent layout (so now simple flow)
		# => alternative position pattern
		elif isinstance(op, changeType):
			print("Pivot:", op.from_type, op.to_type)
			pattern_results.append(["Pivot", op.from_type, op.to_type])
		elif isinstance(op, changeChildrenOrder):
			from_ids = []
			to_ids = []
			for child in op.from_order:
				from_ids.append(child.widget_id)
			for child in op.to_order:
				to_ids.append(child.widget_id)
			print("Change children order:", from_ids, to_ids)
			pattern_results.append(["Change Children Order", from_ids, to_ids])

		elif isinstance(op, moveNode) and op.from_node not in added_children_list \
				and op.to_node not in added_children_list: ##### did not check the order in added flow part
			print("Alternative position:", op.from_node.widget_id, op.to_node.widget_id)
			pattern_results.append(["Alternative Position", op.from_node.widget_id])

	return pattern_results
			



