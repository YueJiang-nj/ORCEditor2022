#
# This file is used to trigger GUI layout resize,
# and returns all the widgets info in the window
#

import time
ERROR_THRESHOD = 5


class Widget():
	def __init__(self, widget_id, left, right, top, \
						bottom, widget_type="Label"):
		self.id = widget_id
		self.type = widget_type
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
		self.left_tabstop = Tabstop("x")
		self.right_tabstop = Tabstop("x")
		self.top_tabstop = Tabstop("y")
		self.bottom_tabstop = Tabstop("y")


class Layout():
	def __init__(self, widget_list, left, right, top, bottom):
		self.widgets = widget_list
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
		self.width = self.right - self.left
		self.height = self.bottom - self.top
		self.left_tabstop = Tabstop("x")
		self.right_tabstop = Tabstop("x")
		self.top_tabstop = Tabstop("y")
		self.bottom_tabstop = Tabstop("y")
		self.widget_dict = {}

	def __copy__(self):
		return Layout(self.widgets, self.left, self.right, \
										self.top, self.bottom)

	def add_widget(self, w):
		self.widgets.append(w)
		self.widget_dict[w.id] = w


class Tabstop():
	def __init__(self, axis):
		self.axis = axis

		# a dict of widget boundaries on the tabstop
		# key is widget, value is left/right/top/bottom
		self.widget_boundaries = {}


# extract widget information
def get_widget_info(widget_group, widget_list):

	# get all the widget in info in this widget group
	for child in widget_group.winfo_children():

		# update the child in the window
		child.update()

		# if the child is not a leaf in the structured tree,
		# recursively check its children 
		if child.winfo_children() != []:
			widget_tabstop_hash = get_children_info(\
								widget_group, widget_list)
		else:
			# extract the id and geometry info of widgets
			widget_name = str(child).split(".")[-1]
			widget_id = int(child.winfo_id())
			widget_type = child.winfo_class()
			widget_size_position = child.winfo_geometry().split("+")
			widget_size = widget_size_position[0].split("x")
			widget_width = int(widget_size[0])
			widget_height = int(widget_size[1])
			widget_left = int(widget_size_position[1])
			widget_right = widget_left + widget_width
			widget_top = int(widget_size_position[2])
			widget_bottom = widget_top + widget_height

			# skip optional widgets
			if widget_right - widget_left == 1 \
					and widget_bottom - widget_top == 1:
				continue

			# save widget with its info in the widget list
			widget = Widget(widget_name, widget_left, widget_right,\
							 widget_top, widget_bottom, widget_type)
			widget_list.append(widget)
			
	return widget_list
	

# given window size, extract tabstops around widgets in the window
def wigdet_info_extraction(window_width, window_height):

	# resize thw window
	root.geometry(str(window_width) + "x" + str(window_height))
	main(window_width, window_height)

	# retrive to get the list of widgets in the layout
	widget_list = []
	widget_list = get_widget_info(root, widget_list)

	# save widgets in the layout
	layout = Layout(widget_list, window_width, window_height)
	
	return layout


# create widget mapping from one layout to the other
def widget_mapping(L1, L2):

	# create widget mapping
	widget_map = {}

	# keep track of residual widgets
	L1_residual_widgets = L1.widgets.copy()
	L2_residual_widgets = L2.widgets.copy()

	# construct widget mapping from L1 to L2
	for w1 in L1.widgets:

		for w2 in L2_residual_widgets:

			# if the two widgets have the same id, 
			# then we add a mapping between them
			if w1.id == w2.id:
				widget_map[w1] = w2

				# remove them from the residual lists
				L1_residual_widgets.remove(w1)
				L2_residual_widgets.remove(w2)

	return widget_map, L1_residual_widgets, L2_residual_widgets


def tabstop_creation(L):

	# initialize tabstop functions
	xtabs = {L.left: L.left_tabstop, L.right: L.right_tabstop}
	ytabs = {L.top: L.top_tabstop, L.bottom: L.bottom_tabstop}

	i = 1
	# add tabstops to the functions
	for w in L.widgets:
		print("widget tabstops:", w.left, w.right, w.top, w.bottom)
		i += 1

		# add left tabstop of the widget
		for x in xtabs.keys():
			existing_tab = False
			if abs(w.left - x) <= ERROR_THRESHOD:
				existing_tab = True
				assigned_xtab = x
		if existing_tab:
			w.left_tabstop = xtabs[assigned_xtab]
		else:
			xtabs[w.left] = w.left_tabstop

		# add right tabstop of the widget
		for x in xtabs.keys():
			existing_tab = False
			if abs(w.right - x) <= ERROR_THRESHOD:
				existing_tab = True
				assigned_xtab = x
		if existing_tab:
			w.right_tabstop = xtabs[assigned_xtab]
		else:
			xtabs[w.right] = w.right_tabstop

		# add top tabstop of the widget
		for y in ytabs.keys():
			existing_tab = False
			if abs(w.top - y) <= ERROR_THRESHOD:
				existing_tab = True
				assigned_ytab = y
		if existing_tab:
			w.top_tabstop = ytabs[assigned_ytab]
		else:
			ytabs[w.top] = w.top_tabstop

		# add bottom tabstop of the widget
		for y in ytabs.keys():
			existing_tab = False
			if abs(w.bottom - y) <= ERROR_THRESHOD:
				existing_tab = True
				assigned_ytab = y
		if w.bottom in ytabs.keys():
			w.bottom_tabstop = ytabs[assigned_ytab]
		else:
			ytabs[w.bottom] = w.bottom_tabstop

		# add widgets to corresponding tabstops
		w.left_tabstop.widget_boundaries[w] = "left"
		w.right_tabstop.widget_boundaries[w] = "right"
		w.top_tabstop.widget_boundaries[w] = "top"
		w.bottom_tabstop.widget_boundaries[w] = "bottom"

	return xtabs, ytabs

# create tabstop mapping
def tabstop_mapping(widget_map, xtabs, ytabs):

	# initialize tabstop mapping
	tab_map = {}

	# initalize mismatched tabstop list as empty 
	mismatched_xtabs = {}
	mismatched_ytabs = {}

	# initalize residual tabstop list containing all the tabstops 
	# in the image of the widget map.
	residual_xtabs = list(xtabs.values())
	residual_ytabs = list(ytabs.values())

	# add new mappings to tabstop map
	for w1 in widget_map.keys():
		w2 = widget_map[w1]

		# if the tabstop is not in the tabstop map,
		# then add a mapping from the tabstop of w1 
		# to the corresponding tabstop of w2 
		if w1.left_tabstop not in tab_map.keys():
			tab_map[w1.left_tabstop] = w2.left_tabstop
			if w2.left_tabstop in residual_xtabs:
				residual_xtabs.remove(w2.left_tabstop) 

		# if an mismatched mapping is found, 
		# then record it in mismatched tabstop list
		elif tab_map[w1.left_tabstop] != w2.left_tabstop:
			if w2.left_tabstop not in mismatched_xtabs:	
				mismatched_xtabs[w2.left_tabstop] = tab_map[w1.left_tabstop]

		# if the tabstop is not in the tabstop map,
		# then add a mapping from the tabstop of w1 
		# to the corresponding tabstop of w2 
		if w1.right_tabstop not in tab_map.keys():
			tab_map[w1.right_tabstop] = w2.right_tabstop
			if w2.right_tabstop in residual_xtabs:
				residual_xtabs.remove(w2.right_tabstop) 

		# if an mismatched mapping is found, 
		# then record it in mismatched tabstop list
		elif tab_map[w1.right_tabstop] != w2.right_tabstop:
			if w2.right_tabstop not in mismatched_xtabs:	
				mismatched_xtabs[w2.right_tabstop] = tab_map[w1.right_tabstop]

		# if the tabstop is not in the tabstop map,
		# then add a mapping from the tabstop of w1 
		# to the corresponding tabstop of w2 
		if w1.top_tabstop not in tab_map.keys():
			tab_map[w1.top_tabstop] = w2.top_tabstop
			if w2.top_tabstop in residual_ytabs:
				residual_ytabs.remove(w2.top_tabstop) 

		# if an mismatched mapping is found, 
		# then record it in mismatched tabstop list
		elif tab_map[w1.top_tabstop] != w2.top_tabstop:
			if w2.top_tabstop not in mismatched_ytabs:
				mismatched_ytabs[w2.top_tabstop] = tab_map[w1.top_tabstop]

		# if the tabstop is not in the tabstop map,
		# then add a mapping from the tabstop of w1 
		# to the corresponding tabstop of w2 
		if w1.bottom_tabstop not in tab_map.keys():
			tab_map[w1.bottom_tabstop] = w2.bottom_tabstop
			if w2.bottom_tabstop in residual_ytabs:
				residual_ytabs.remove(w2.bottom_tabstop) 

		# if an mismatched mapping is found, 
		# then record it in mismatched tabstop list
		elif tab_map[w1.bottom_tabstop] != w2.bottom_tabstop:
			if w2.bottom_tabstop not in mismatched_ytabs:	
				mismatched_ytabs[w2.bottom_tabstop] = tab_map[w1.bottom_tabstop]

	return mismatched_xtabs, mismatched_ytabs, \
			residual_xtabs, residual_ytabs


# check whether widgets in the two layouts are equivalent
def widget_equivalence_check(L1_residual_widgets, L2_residual_widgets):

	# if there are residual widgets, then they are not equivalent
	if L1_residual_widgets or L2_residual_widgets:
		return False

	# if no residual widgets exists, then they are equivalent
	else:
		return True


# check whether tabstops in the two layouts are equivalent
def tabstop_equivalence_check(L1, L2, widget_map):

	# get all the tabstops in both layouts
	xtabs1, ytabs1 = tabstop_creation(L1)
	xtabs2, ytabs2 = tabstop_creation(L2)

	# create tabstop map from L1 to L2
	mismatched_xtabs2, mismatched_ytabs2, residual_xtabs2, \
		residual_ytabs2 = tabstop_mapping(widget_map, xtabs2, ytabs2)

	# get the inverse mapping of the widget map
	widget_map_inverse = {}
	for key in widget_map.keys():
		value = widget_map[key]
		widget_map_inverse[value] = key

	# create tabstop map from L2 to L1
	mismatched_xtabs1, mismatched_ytabs1, residual_xtabs1, \
			residual_ytabs1 = tabstop_mapping(widget_map_inverse,\
												 xtabs1, ytabs1)

	# remove residual tabstops from the set of keys of mismatched tabstops
	diff_xtab1 = set(mismatched_xtabs1.keys()) - set(residual_xtabs1)
	diff_ytab1 = set(mismatched_ytabs1.keys()) - set(residual_ytabs1)
	diff_xtab2 = set(mismatched_xtabs2.keys()) - set(residual_xtabs2)
	diff_ytab2 = set(mismatched_ytabs2.keys()) - set(residual_ytabs2)

	# add tabstops in mismatched hash map conflicted with the tabstops in the sets
	diff_xtab1_final = diff_xtab1.copy()
	diff_ytab1_final = diff_ytab1.copy()
	diff_xtab2_final = diff_xtab2.copy()
	diff_ytab2_final = diff_ytab2.copy()
	for tab in diff_xtab1:
		diff_xtab1_final.add(mismatched_xtabs1[tab])
	for tab in diff_ytab1:
		diff_ytab1_final.add(mismatched_ytabs1[tab])
	for tab in diff_xtab2:
		diff_xtab2_final.add(mismatched_xtabs2[tab])
	for tab in diff_ytab2:
		diff_ytab2_final.add(mismatched_ytabs2[tab])

	# if all the diff sets are empty, then the tabstops in the 
	# two layouts are topologically equivalent
	return diff_xtab1_final, diff_ytab1_final, \
			diff_xtab2_final, diff_ytab2_final

# check whether topologies of the two layouts are equivalent
def topological_equivalence_check(L1, L2):

	# get widget map and the residual widget lists
	widget_map, L1_residual_widgets, L2_residual_widgets \
						= widget_mapping(L1, L2)

	# check whether widgets and tabstops are equivalent
	widget_equivalence = widget_equivalence_check( \
				L1_residual_widgets, L2_residual_widgets)
	diff_xtab1_final, diff_ytab1_final, diff_xtab2_final, \
					diff_ytab2_final = tabstop_equivalence_check( \
											L1, L2, widget_map)
	tabstop_equivalence = (len(diff_xtab1_final) == 0) \
							and (len(diff_ytab1_final) == 0) \
							and (len(diff_xtab2_final) == 0) \
							and (len(diff_ytab2_final) == 0) 

	# two layouts are topologically equivalent if and only
	# if both widgets and tabstops are equivalent
	if widget_equivalence and tabstop_equivalence:
		return True
	else: 
		return False


if __name__ == "__main__":

	# run GUI layout
	run_layout()

	window_width1 = 320 + 160
	window_height1 = 400
	window_width2 = 640 + 320
	window_height2 = 320
	window_width1 = 320
	window_height1 = 400
	window_width2 = 320
	window_height2 = 640

	# # 1 row
	window_width1 = 640
	window_height1 = 560
	# # window_width2 = 700
	# # window_height2 = 560

	# # 4 rows
	window_width1 = 160
	window_height1 = 720

	# # # 2 row
	window_width2 = 320
	window_height2 = 480

	### 12 ###
	# 2 rows
	window_width1 = 6 * 80
	window_height1 = (2 + 3) * 80

	# 3 rows
	window_width1 = 4 * 80
	window_height1 = (3 + 3) * 80

	# 4 rows
	window_width2 = 3 * 80
	window_height2 = (4 + 3) * 80

	window_width1 = 8 * 80
	window_height1 = (1 + 3) * 80 

	window_width2 = 10 * 80
	window_height2 = (1 + 3) * 80 

	L1 = wigdet_info_extraction(window_width1, window_height1)
	time.sleep(5)
	L2 = wigdet_info_extraction(window_width2, window_height2)
	
	time.sleep(1)
