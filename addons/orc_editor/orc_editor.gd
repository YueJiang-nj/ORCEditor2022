extends Control
tool


var json_helper = preload("./json_helper.gd")


# inistialize the size options
func _ready():
	
	# add recommended window sizes
	$sizes.get_popup().clear()
	$sizes.get_popup().add_item("Landscape (16:9)")
	$sizes.get_popup().add_item("Landscape (4:3)")
	$sizes.get_popup().add_item("Portrait")
	$sizes.get_popup().connect("id_pressed", self, "_on_item_pressed_recommended_window_size")


# called whenever scene size got changed
func _on_scene_changed(scene_root : Node):
	print(scene_root.name)
	scene_root.connect("item_rect_changed", self, "_on_item_rect_changed", [scene_root])
	

func _on_item_pressed_recommended_window_size(id):
	
	# get the current scene root node
	var root = get_tree().get_edited_scene_root()
	
	# get selected items
	var item_name = $sizes.get_popup().get_item_text(id)
	var window_width
	var window_height
	print("select")
	
	# case 1: Landscape (16:9)
	if item_name == "Landscape (16:9)":
		window_width = 40 * 16
		window_height = 40 * 9
		print(item_name)
	
	# case 2: Landscape (4:3)
	elif item_name == "Landscape (4:3)":
		window_width = 150 * 4
		window_height = 150 * 3
		print(item_name)
		
	# case 3: Portrait
	elif item_name == "Portrait":
		window_width = 53 * 9
		window_height = 50 * 12
		print(item_name)
		
	# get updated layout info according to the window size
	var updated_layout_info = update_view(window_width, window_height)
	
	# update layout based on updated layout info
	update_layout(root, updated_layout_info)

# given a window size, update view
func update_view(window_width, window_height):
	
	#  store updated layout info
	var updated_layout_info
	
	# if only the first view got saved,
	# then we detect flows and orclayout initialization
	var stdout = []
	OS.execute("python3", ["./Code/godot_solve_orclayout_specification.py", 
			window_width, window_height, len($Globals.view_list) ], true, stdout, true)
	
	# load the produced result from ORCSolver
	updated_layout_info = json_helper.load_json("./initialization_inference.json")
	
	return updated_layout_info
	
# update shown layout based on updated layout info
func update_layout(root, updated_layout_info):
	
#	# update widget positions and sizes
	for child in root.get_children():
		if child.get_class() ==  "PopupDialog" or child.get_class() ==  "Line2D":
			child.visible = false
			continue
		var c : Control = child
		var widget_name = c.get_name()
		if updated_layout_info.has(widget_name):
			c.rect_position.x = updated_layout_info[widget_name]["x"]
			c.rect_position.y = updated_layout_info[widget_name]["y"]
			c.rect_size.x = updated_layout_info[widget_name]["width"]
			c.rect_size.y = updated_layout_info[widget_name]["height"]	
		else:
			c.rect_position.x =  -1000
			c.rect_position.y =  -1000
			c.rect_size.x = 0
			c.rect_size.y = 0
	
	if $Globals.flow_visualization:
		_on_visualize_flows()
		
	if $Globals.constraint_visualization:
		_on_visualize_constraints()
	

# get current layout info and write into the json file
func layout_info_to_json(root):

	# initialization
	var layout_info = {}
	
	# add layout size information
	layout_info["root"] = {"width": root.rect_size.x,
						  "height": root.rect_size.y}
					
	# add widget information
	# we only allow two layers now
	for child in root.get_children():
		if child.get_class() ==  "PopupDialog":
			continue
		
		# make sure child is a Control
		if not child is Control:
			continue
		
		if "Container" in child.get_class():
			for child_in_container in child.get_children():
				
				# make sure child is a Control
				if not child_in_container is Control:
					continue
				
				var c : Control = child_in_container
				layout_info[c.get_name()] = {"x": c.rect_position.x,
											"y": c.rect_position.y, 
											"width": c.rect_size.x, 
											"height": c.rect_size.y}
		else:
			var c : Control = child
			layout_info[c.get_name()] = {"x": c.rect_position.x,
										"y": c.rect_position.y, 
										"width": c.rect_size.x, 
										"height": c.rect_size.y}
			
			
	# add the first view to the view list
	var scene_name = root.get_name()
	if not $Globals.view_list.has(scene_name):
		$Globals.view_list.append(scene_name)
									
	# save layout information to a JSON file
	var json_path = "./json_files/" + scene_name + ".json"
	json_helper.write_json(layout_info, json_path)#########
	
	# print message to show first view saved
	var message = "The view " + scene_name + " got saved!\n" \
		+ "The current view list is " + str($Globals.view_list) + "."
	$update.set_text(message)


# get triggered when the view gets resized
func _on_item_rect_changed(node : Control):
	print("rect of control %s changed to %s / %s" % [node.name, str(node.rect_position), str(node.rect_size)])
	
	# get the current scene root node
	var root = get_tree().get_edited_scene_root()
	
	# add layout size information
	var window_width = root.rect_size.x
	var window_height = root.rect_size.y
	
	for c in root.get_children():
		if c.name == "1":
			c.rect_position.x = 200 + (window_width - 1000) * 2 / 6
			c.rect_position.y = 200
			c.rect_size.x = 200
			c.rect_size.y = 100
			
		if c.name == "2":
			c.rect_position.x = 600 + (window_width - 1000) * 4 / 6
			c.rect_position.y = 200
			c.rect_size.x = 200
			c.rect_size.y = 100
	
	
	return
	
	
	if root.get_name() == "grid_flow":
		print("grid_flow")
		var w = 0
		var h = 0
		
		# horizontal grid flow
		if window_width > window_height:
			w = window_width / 6
			h = window_height / 3
			
			# update widget positions and sizes
			for child in root.get_children():
				if child.get_class() ==  "PopupDialog":
					continue
				var c : Control = child

				c.rect_position.x = (int(c.get_name()) - 1) % 6 * w
				c.rect_position.y = (int(c.get_name()) - 1) / 6 * h
				c.rect_size.x = w
				c.rect_size.y = h
		else:
			w = window_width / 3
			h = window_height / 6
			
			# update widget positions and sizes
			for child in root.get_children():
				if child.get_class() ==  "PopupDialog":
					continue
				var c : Control = child
					
				c.rect_position.x = (int(c.get_name()) - 1) % 3 * w
				if int(c.get_name()) <= 3:
					c.rect_position.y = h * 0
				elif int(c.get_name()) <= 6:
					c.rect_position.y = h * 3
				elif int(c.get_name()) <= 9:
					c.rect_position.y = h * 1
				elif int(c.get_name()) <= 12:
					c.rect_position.y = h * 4
				elif int(c.get_name()) <= 15:
					c.rect_position.y = h * 2
				elif int(c.get_name()) <= 18:
					c.rect_position.y = h * 5
				c.rect_size.x = w
				c.rect_size.y = h
	else:
		# get updated layout info according to the window size
		var updated_layout_info = update_view(window_width, window_height)
		
		# update layout based on updated layout info
		update_layout(root, updated_layout_info)


# get widget info message from widget info regarding flows
func get_widget_info_message(root):
	
	# get widget info regarding flows
	var widget_info = json_helper.load_json("./widget_info.json")
	
	# update widget positions and sizes
	for child in root.get_children():
		if child.get_class() ==  "PopupDialog":
			continue
		var widget_id = child.get_name()
		var message = child.get_class() + " " + child.get_name() + ":\n"
		var error_message = child.get_class() + " " + child.get_name() + ":"
		var widget_flow_info = widget_info[widget_id]
		if widget_flow_info["flow_type"] != "":
			message += "In a " + widget_flow_info["flow_type"] \
				+ " containing widgets " 
			
			# add widget elements in the flow
			var flow_elements = widget_flow_info["flow_elements"]
			message += flow_elements[0]
			for i in range(1, len(flow_elements)):
				message += ", " + flow_elements[i]
			
			# add optional widget elements in the flow	
			var num_widgets = len(widget_flow_info["optional_elements"])
			if num_widgets > 0:
				if num_widgets == 1:
					message += " with an optional widget "
				else:
					message += " with optional widgets " 
				var optional_elements = widget_flow_info["optional_elements"]
				message += optional_elements[0]
				for i in range(1, len(optional_elements)):
					message += ", " + optional_elements[i]
		message += ".\n"
		$Globals.widget_message[widget_id] = message
		$Globals.widget_error_message[widget_id] = error_message
	return widget_info

# get triggered when the button Save First View gets pressed
func _save_first_view_pressed():
	
	# get current layout info and write into a json file
	var root = get_tree().get_edited_scene_root()
	$Globals.view_list = []
	layout_info_to_json(root) 
	
	# get window size
	var window_width = root.rect_size.x
	var window_height = root.rect_size.y
									
	# get the json file path
	var json_path = "./json_files/" + root.get_name() + ".json"
	
	# run ORCSolver to get optimized widget positions and sizes
	var stdout = []
	OS.execute("python3", ["./Code/godot_first_view_initialization.py", json_path, 
			window_width, window_height], true, stdout, true)
	print("===", stdout)
	

	# get widget info message from widget info regarding flows
	get_widget_info_message(root)

func _add_update_view_pressed():
	
	# get current layout info and write into a json file
	var root = get_tree().get_edited_scene_root()
	print($Globals.view_list)
	layout_info_to_json(root)
	root.set_name("UI2")#######
#
	# run ORCSolver to update optimized widget positions and sizes
	OS.execute("python3", ["./Code/godot_update_orclayout_specification.py", $Globals.view_list], true, [], true)
	
	# get widget info message from widget info regarding flows
	var widget_info = get_widget_info_message(root)
	
	# get optional elements
	var file = File.new()
	file.open("./element_diff/optional_elements.txt", File.READ)
	var content = file.get_as_text().strip_edges()
	file.close()
	var optional_elements = content.split(" ") 
	if len(content) > 0:
		for element in optional_elements:
			print("Detected optional widget " + element)
		
	# get misordered elements
	file.open("./element_diff/misordered_elements.txt", File.READ)
	content = file.get_as_text().strip_edges()
	file.close()
	var misordered_elements = content.split(" ") 
	var theme = load("res://addons/orc_editor/red_color.tres")
	if len(content) > 0:
		for element in misordered_elements:
			root.get_node(element).set_theme(theme)
			print("Detected misordered widget " + element)
			var error_message = $Globals.widget_error_message[element]
			error_message += "\nDetected potential misordered elements " \
				+ str(misordered_elements) + ".\nDo you want to reorder?"
			$Globals.widget_error_message[element] = error_message
		
	# get misordered elements
	file.open("./element_diff/mispositioned_elements.txt", File.READ)
	content = file.get_as_text().strip_edges()
	file.close()
	var mispositioned_elements = content.split(" ") 
	if len(content) > 0:
		for element in mispositioned_elements:
			print("Detected mispositioned widget " + element)
	
	
# preview the result
func _on_preview_pressed():
	print("===== preview =====")

	# get the layout root
	var root = get_tree().get_edited_scene_root()

#	# update layout based on updated layout info
#	for updated_layout_info in $Globals.updated_layout_info_list:
#		update_layout(root, updated_layout_info)
#		yield(get_tree().create_timer(0.06), "timeout")

#var width_min = 340
#	var height_min = 360
#	var width_max = 700
#	var height_max = 600
#
	var width_min = 340
	var height_min = 600


	# get updated layout info according to the window size
	var updated_layout_info = update_view(width_min, height_min)

	# update layout based on updated layout info
	update_layout(root, updated_layout_info)
#

# save preview info into an array to reload later
func _on_preview_preparation_pressed():
	
	var window_width = 0
	var window_height = 0
	$Globals.updated_layout_info_list = []
	var width_min = 340
	var height_min = 360
	var width_max = 700
	var height_max = 600
	var step = 10
	
	# horizontal preview 
	window_height = height_min
	for size in range(width_min, width_max + 1, step):
		print(size)
		window_width = size
		print(window_width,window_height)

		# get updated layout info according to the window size
		$Globals.updated_layout_info_list.append(update_view(window_width, window_height))

	# vertical preview 
	window_width = width_max
	for size in range(height_min + step, height_max + 1, step):
		print(size)
		window_height = size
		print(window_width,window_height)

		# get updated layout info according to the window size
		$Globals.updated_layout_info_list.append(update_view(window_width, window_height))

	# diagonal preview
	var mini_step = 5
	for size in range(height_max - step, height_min - 1, -step):
		print(size)
		window_width = size - (height_max - width_max) - mini_step
		window_height = size
		print(window_width,window_height)
		mini_step += 5

		# get updated layout info according to the window size
		$Globals.updated_layout_info_list.append(update_view(window_width, window_height))

	# vertical preview
	window_width = width_min
	for size in range(height_min + step, height_max + 1, step):
		print(size)
		window_height = size
		print(window_width,window_height)

		# get updated layout info according to the window size
		$Globals.updated_layout_info_list.append(update_view(window_width, window_height))

	# horizontal preview 
	window_height = height_max
	for size in range(width_min + step, width_max + 1, step):
		print(size)
		window_width = size
		print(window_width,window_height)

		# get updated layout info according to the window size
		$Globals.updated_layout_info_list.append(update_view(window_width, window_height))

#
#func draw_dashed_line(from, to, color, width, dash_length = 5, cap_end = false, antialiased = false):
#	var length = (to - from).length()
#	var normal = (to - from).normalized()
#	var dash_step = normal * dash_length
#
#	if length < dash_length: #not long enough to dash
##		draw_line(from, to, color, width, antialiased)
#		return
#
#	else:
#		var draw_flag = true
#		var segment_start = from
#		var steps = length/dash_length
#		for start_length in range(0, steps + 1):
#			var segment_end = segment_start + dash_step
#			if draw_flag:
#				draw_line(segment_start, segment_end, color, width, antialiased)
#
#			segment_start = segment_end
#			draw_flag = !draw_flag
#
#		if cap_end:
#			draw_line(segment_start, to, color, width, antialiased)

func _on_ORC_Update_pressed():
	
	# get the layout root
	var root = get_tree().get_edited_scene_root()
	
	var widget_info = json_helper.load_json("./widget_info.json")
	
	# load the produced result from ORCSolver
	var updated_layout_info = json_helper.load_json("./initialization_inference.json")
	
	
#	# get updated layout info according to the window size
#	var window_width = root.rect_size.x
#	var window_height = root.rect_size.y
#	var updated_layout_info = update_view(window_width, window_height)
#
#	# update layout based on updated layout info
#	update_layout(root, updated_layout_info)
	
	print(widget_info)

	var used_widgets = []
	for child in root.get_children():
		var widget_id = child.get_name()
		var widget_flow_info = widget_info[widget_id]
		if not used_widgets.has(widget_id):
			var orc_structure 

			# detect possible horizontal flows and create ORCRow
			if widget_flow_info["flow_type"] == "Horizontal Flow":
				orc_structure = ORCRow.new()
				
				
			# detect possible vertical flows and create ORCColumn
			elif widget_flow_info["flow_type"] == "Vertical Flow":
				orc_structure = ORCColumn.new()
#				root.add_child(orc_structure)
#				orc_structure.set_owner(root)
#				orc_structure.set_name(widget_flow_info["flow_name"])

			if "Flow" in widget_flow_info["flow_type"]:
				print("44444")
				root.add_child(orc_structure)
				orc_structure.set_owner(root)
				var flow_name = widget_flow_info["flow_name"]
				orc_structure.set_name(flow_name)
				
#				var line = Line2D.new()
#				orc_structure.add_child(line)
#				line.set_owner(root)
#				var points: PoolVector2Array = PoolVector2Array()
##				points.append(Vector2(10, 10))
##				points.append(Vector2(100, 100))
##				line.add_point(points[0])
##				line.add_point(points[1])
#				line_list,
#				draw_dashed_line(Vector2(300, 500), Vector2(519, 500), Color(1, 1, 1, 1), 5, 10, false)
#				draw_line(points[0], points[1], Color(1, 1, 1, 1), 5, false)
				orc_structure.rect_position.x = updated_layout_info[flow_name]["x"]
				orc_structure.rect_position.y = updated_layout_info[flow_name]["y"]
				orc_structure.rect_size.x = updated_layout_info[flow_name]["width"]
				orc_structure.rect_size.y = updated_layout_info[flow_name]["height"]
				print(flow_name, orc_structure.rect_position, orc_structure.rect_size)

			# put all the elements in the orc structure
			for id in widget_flow_info["flow_elements"]:
				used_widgets.append(id)

#				# move elements into the orc structure
#				var node = root.find_node(id)
#				root.remove_child(node)
#				orc_structure.add_child(node)
#				node.set_owner(root)

			if widget_flow_info["flow_type"] == "Horizontal Flow":
				var hf_left = []
				var hf_right = []
				var hf_middle_line = []
				var left = 1000000
				var right = 1000000
				var middle_line = -1000000
				var num = 0
				for id in widget_flow_info["flow_elements"]:
					var x = updated_layout_info[id]["x"] 
					var y = updated_layout_info[id]["y"] 
					var width = updated_layout_info[id]["width"] 
					var height = updated_layout_info[id]["height"] 
					if x + 5 < right:
						left = x
						hf_left.append(left)
						right = x + width
						hf_right.append(right)
						if hf_middle_line != []:
							hf_middle_line[-1] /= num	
						hf_middle_line.append(y + height / 2)
						num = 1
					else:
						right = x + width
						hf_right[-1] = right
						hf_middle_line[-1] += y + height / 2
						num += 1
				hf_middle_line[-1] /= num	
				print("00",hf_left, hf_right, hf_middle_line)
				var current_num_lines = len($Globals.line_list)
		
				for i in len(hf_left):
					var point0 = Vector2(hf_left[i], hf_middle_line[i])
					var point1 = Vector2(hf_right[i], hf_middle_line[i])
					
					# for drawing arrows
					var point2 = Vector2(hf_right[i] - 15, hf_middle_line[i] + 5)
					var point3 = Vector2(hf_right[i] - 15, hf_middle_line[i] - 5)
#					var point4 = Vector2(hf_right[i] + 2, hf_middle_line[i] + 2)
					if i < current_num_lines:
						$Globals.line_list[i].set_point_position(0, point0)
						$Globals.line_list[i].set_point_position(1, point1)
						$Globals.line_list[i].set_point_position(2, point2)
						$Globals.line_list[i].set_point_position(3, point3)
						$Globals.line_list[i].set_point_position(4, point1)
						
						$Globals.line_list[i].visible = true
					else:
						var line = Line2D.new()
						line.set_width(5)
						root.add_child(line)
						line.set_owner(root)
						line.add_point(point0)
						line.add_point(point1)
						line.add_point(point2)
						line.add_point(point3)
						line.add_point(point1)
						$Globals.line_list.append(line)
					if i < len(hf_left) - 1:
						var point_dot = Vector2(hf_left[i+1], hf_middle_line[i+1])
						if i < current_num_lines  - 1:
							$Globals.dotted_line_list[i].set_point_position(0, point1)
							$Globals.dotted_line_list[i].set_point_position(1, point_dot)
							$Globals.dotted_line_list[i].visible = true
#							var color = $Globals.dotted_line_list[i].get_default_color()
#							color[-1] = 0.3
#							$Globals.dotted_line_list[i].set_default_color(color)
						else:
							var line = Line2D.new()
							root.add_child(line)
							line.set_owner(root)
							line.add_point(point1)
							line.add_point(point_dot)
							var color = line.get_default_color()
							color[-1] = 0.3
							line.set_default_color(color)
							$Globals.dotted_line_list.append(line)
						
				for i in range(len(hf_left), current_num_lines):
					$Globals.line_list[i].visible = false
				for i in range(len(hf_left) - 1, current_num_lines - 1):
					$Globals.dotted_line_list[i].visible = false
#				$Globals.line_list[-1].visible = false
#				$Globals.line_list = []
#				$Globals.dotted_line_list = []
#			elif widget_flow_info["flow_type"] == "Vertical Flow":
					
#
#
					
			
		
			
#
#		var message = child.get_class() + " " + child.get_name() + ":\n"
#		var error_message = child.get_class() + " " + child.get_name() + ":"
#		var widget_flow_info = widget_info[widget_id]
#		if widget_flow_info["flow_type"] != "":
#			message += "In a " + widget_flow_info["flow_type"] \
#				+ " containing widgets " 
#	child = ORCRow.new()

#	var parent
#	var child
#	for c in root.get_children():
#		var widget_name = c.get_name()
#		if  widget_name == "1":
#			parent = c
#		if widget_name == "4":
#			child = c
#
#	root.remove_child(child)
#	parent.add_child(child)
#	child.set_owner(root)
	

	
	
	
	
	
	
	
	
	
	
	
	
#	# get the layout root
#	var root = get_tree().get_edited_scene_root()
#
#	# add layout size information
#	var window_width = root.rect_size.x
#	var window_height = root.rect_size.y
#
#	for child in root.get_children():
#		print("Container" in child.get_class())
#
#	# get updated layout info according to the window size
#	var updated_layout_info = update_view(window_width, window_height)
##	print(updated_layout_info)
##	print($Globals.view_list)
#	var parent
#	var child
#	for c in root.get_children():
#		var widget_name = c.get_name()
#		if  widget_name == "1":
#			parent = c
#		if widget_name == "C":
#			child = c
#	child = Button.new()
#	#root.remove_child(child)
#	root.add_child(child)
#	#child.set_owner(parent)
#
#	var node = ORCRow.new()
#	node.set_name("yue1")
#	# the parent can be get_tree().get_root() or some other node
#	parent.add_child(node)
#	# ownership is different, I think it's not the same root as the root node
#	node.set_owner(root)
	
	
			
	

#	var node = ORCRow.new()
#	node.set_name("ORCRow1")
#	# the parent can be get_tree().get_root() or some other node
#	root.add_child(node)
#	# ownership is different, I think it's not the same root as the root node
#	node.set_owner(root)
#	node.rect_position.x = updated_layout_info["HF"]["x"]
#	node.rect_position.y = updated_layout_info["HF"]["y"]
#	node.rect_size.x = updated_layout_info["HF"]["width"]
#	node.rect_size.y = updated_layout_info["HF"]["height"]
#	for c in root.get_children():
#		var widget_name = c.get_name()
#		if  widget_name == "1" or widget_name == "2" \
#				or widget_name == "3" or widget_name == "4" \
#				or widget_name == "5" or widget_name == "6" \
#				or widget_name == "7" or widget_name == "8":
#			root.remove_child(c)
#			node.add_child(c)
#			#c.set_owner(node)
			
#		if  widget_name == "A" or widget_name == "B" \
#					or widget_name == "C" or widget_name == "D" \
#					or widget_name == "E" or widget_name == "F":
		
#
#	# update layout based on updated layout info
#	update_layout(root, updated_layout_info)
	
#	# update widget positions and sizes
#	for child in root.get_children():
#		if "Container" in child.get_class():
#			for child_in_container in child.get_children():
#
#				# make sure child is a Control
#				if not child_in_container is Control:
#					continue
#
#				var c : Control = child_in_container
#				updated_layout_info[c.get_name()] = {"x": c.rect_position.x,
#											"y": c.rect_position.y, 
#											"width": c.rect_size.x, 
#											"height": c.rect_size.y}
#		else:
#			if child.get_class() ==  "PopupDialog":
#				continue
#			var c : Control = child
#			var widget_name = c.get_name()
#
#			if updated_layout_info.has(widget_name):
#				c.rect_position.x = updated_layout_info[widget_name]["x"]
#				c.rect_position.y = updated_layout_info[widget_name]["y"]
#				c.rect_size.x = updated_layout_info[widget_name]["width"]
#				c.rect_size.y = updated_layout_info[widget_name]["height"]
#				########
#				if widget_name == "A" or widget_name == "B" \
#					or widget_name == "C" or widget_name == "D" \
#					or widget_name == "E" or widget_name == "F":
#					if c.rect_position.x == 0:
#						c.rect_position.x = updated_layout_info["1"]["x"]
#					else:
#						c.rect_position.x = updated_layout_info["2"]["x"]
#					c.rect_size.x = updated_layout_info["1"]["width"]
#

	
#	var __body_parent : Node = body.get_parent()
#__body_parent.remove_child(body)
#bullet.add_child(body)
#
#	var node = ORCRow.new()
#	node.set_name("yue")
#	# the parent can be get_tree().get_root() or some other node
#	root.add_child(node)
#	# ownership is different, I think it's not the same root as the root node
#	node.set_owner(root)
	
	
	
	

func _on_visualize_flows():
	
#	print("yyusssss    ", len($Globals.vis_flow_trangles["HF"]))
	
	# set visualization variables
	$Globals.flow_visualization = true
#	$Globals.constraint_visualization = false
	
	# get the layout root
	var root = get_tree().get_edited_scene_root()
	
	# get widget info including flow_elements, flow type, etc.
	var widget_info = json_helper.load_json("./widget_info.json")
#	$Globals.vis_flow_trangles = {}
#	return

	# load the produced result from ORCSolver
	# e.g., Text:{height:481, width:372, x:80, y:160}, 
	# VF:{height:481, width:80, x:0, y:160}, window_height:641, window_width:452}
	var updated_layout_info = json_helper.load_json("./initialization_inference.json")

	# visualize all the flows
	var used_widgets = []
	var i = -1
	for child in root.get_children():
		var widget_id = child.get_name()
		
		# skip optional widgets
		if not (widget_id in widget_info):
			continue
			
		# get all the flow information
		var widget_flow_info = widget_info[widget_id]
		if not used_widgets.has(widget_id):

			# record all the used elements
			for id in widget_flow_info["flow_elements"]:
				used_widgets.append(id)
				
			# skip non flow elements
			if not "flow_name" in widget_flow_info:
				continue

			# get the  flow name
			var flow_name = widget_flow_info["flow_name"]
			
			# create triangles for the current flow
			if not (flow_name in $Globals.vis_flow_trangles):
				$Globals.vis_flow_trangles[flow_name] = []
				
			# get the line points for the lines and dotted lines
			var flow_end1 = [] 
			var flow_end2 = []
			var flow_middle_line = []
			var end1 = 1000000
			var end2 = 1000000
			var middle_line = -1000000
			var num = 0
			print(flow_name, len($Globals.vis_flow_trangles["HF"]))
			var current_num_lines = len($Globals.vis_flow_trangles[flow_name])
			
			for id in widget_flow_info["flow_elements"]:
				
				# skip optional widgets
				if root.find_node(id).rect_position.x == -1000:
					continue
					
				# compute the left, right and positon of the lines
				var x = updated_layout_info[id]["x"] 
				var y = updated_layout_info[id]["y"] 
				var width = updated_layout_info[id]["width"] 
				var height = updated_layout_info[id]["height"] 
				
				var point0
				var point1
				var point2
				var point3
				var w
				var h
				
				# horizontal flow
				if widget_flow_info["flow_type"] == "Horizontal Flow":
					
					# find the right bottom point
					i += 1
					w = x + width
					h = y + height
					point0 = Vector2(w, h)
					point1 = Vector2(w - 23, h)
					point2 = Vector2(w, h - 23)
					point3 = Vector2(w, h)
				print(i, current_num_lines)
				# update the existing arrow lines
				if i < current_num_lines:
					$Globals.vis_flow_trangles[flow_name][i].set_point_position(0, point0)
					$Globals.vis_flow_trangles[flow_name][i].set_point_position(1, point1)
					$Globals.vis_flow_trangles[flow_name][i].set_point_position(2, point2)
					$Globals.vis_flow_trangles[flow_name][i].set_point_position(3, point3)
					$Globals.vis_flow_trangles[flow_name][i].visible = true
					$Globals.vis_flow_trangles[flow_name][i].set_width(13)

				# create new arrow lines
				else:
					var line = Line2D.new()
#					print(line.get_default_color())
					
					# set colors
					var line_color
					if widget_flow_info["flow_type"] == "Horizontal Flow":
						line_color = Color( 0.4, 0.6, 1, 1 )		# blue
					elif widget_flow_info["flow_type"] == "Vertical Flow":
						line_color = Color( 0.4, 0.85, 0.5, 1 )		# green
						
					# create arrow lines
					line.set_width(10)
					line.set_default_color(line_color)
					root.add_child(line)
					line.set_owner(root)
					line.add_point(point0)
					line.add_point(point1)
					line.add_point(point2)
					line.add_point(point3)
					$Globals.vis_flow_trangles[flow_name].append(line)
					print("yyu    ", len($Globals.vis_flow_trangles[flow_name]))
					
			i += 1
			
#			# make all the unused lines invisible
#			for j in range(len(flow_end1), current_num_lines):
#				$Globals.vis_flow_trangles[flow_name][j].visible = false


#
#func _on_visualize_flows():
#
#	# set visualization variables
#	$Globals.flow_visualization = true
##	$Globals.constraint_visualization = false
#
#	# get the layout root
#	var root = get_tree().get_edited_scene_root()
#
#	# get widget info including flow_elements, flow type, etc.
#	var widget_info = json_helper.load_json("./widget_info.json")
#
#	# load the produced result from ORCSolver
#	# e.g., Text:{height:481, width:372, x:80, y:160}, 
#	# VF:{height:481, width:80, x:0, y:160}, window_height:641, window_width:452}
#	var updated_layout_info = json_helper.load_json("./initialization_inference.json")
#
#	# visualize all the flows
#	var used_widgets = []
#	for child in root.get_children():
#		var widget_id = child.get_name()
#
#		# skip optional widgets
#		if not (widget_id in widget_info):
#			continue
#
#		# get all the flow information
#		var widget_flow_info = widget_info[widget_id]
#		if not used_widgets.has(widget_id):
#
#			# record all the used elements
#			for id in widget_flow_info["flow_elements"]:
#				used_widgets.append(id)
#
#			# skip non flow elements
#			if not "flow_name" in widget_flow_info:
#				continue
#
#			# get the  flow name
#			var flow_name = widget_flow_info["flow_name"]
#
#			# create arrow lines and dotted lines for the current flow
#			if not (flow_name in $Globals.line_list):
#				$Globals.line_list[flow_name] = []
#				$Globals.dotted_line_list[flow_name] = []
#
#			# get the line points for the lines and dotted lines
#			var flow_end1 = [] 
#			var flow_end2 = []
#			var flow_middle_line = []
#			var end1 = 1000000
#			var end2 = 1000000
#			var middle_line = -1000000
#			var num = 0
#			for id in widget_flow_info["flow_elements"]:
#
#				# skip optional widgets
#				if root.find_node(id).rect_position.x == -1000:
#					continue
#
#				# compute the left, right and positon of the lines
#				var x = updated_layout_info[id]["x"] 
#				var y = updated_layout_info[id]["y"] 
#				var width = updated_layout_info[id]["width"] 
#				var height = updated_layout_info[id]["height"] 
#
#				# horizontal flow
#				if widget_flow_info["flow_type"] == "Horizontal Flow":
#					if x + 5 < end2:
#						end1 = x
#						flow_end1.append(end1)
#						end2 = x + width
#						flow_end2.append(end2)
#						if flow_middle_line != []:
#							flow_middle_line[-1] /= num	
#						flow_middle_line.append(y + height / 2)
#						num = 1
#					else:
#						end2 = x + width
#						flow_end2[-1] = end2
#						flow_middle_line[-1] += y + height / 2
#						num += 1
#
#				# vertical flow
#				elif widget_flow_info["flow_type"] == "Vertical Flow":
#					if y + 5 < end2:
#						end1 = y
#						flow_end1.append(end1)
#						end2 = y + height
#						flow_end2.append(end2)
#						if flow_middle_line != []:
#							flow_middle_line[-1] /= num
#						flow_middle_line.append(x + width / 2)
#						num = 1
#					else:
#						end2 = y + height
#						flow_end2[-1] = end2
#						flow_middle_line[-1] += x + width / 2
#						num += 1
#			flow_middle_line[-1] /= num
#
#			# update arrow lines and dotted lines 
#			var current_num_lines = len($Globals.line_list[flow_name])
#			for i in len(flow_end1):
#				var point0
#				var point1
#				var point2
#				var point3
#
#				# update arrow lines 
#				# horizontal flow
#				if widget_flow_info["flow_type"] == "Horizontal Flow":
#					point0 = Vector2(flow_end1[i], flow_middle_line[i])
#					point1 = Vector2(flow_end2[i], flow_middle_line[i])
#					point2 = Vector2(flow_end2[i] - 15, flow_middle_line[i] + 5)
#					point3 = Vector2(flow_end2[i] - 15, flow_middle_line[i] - 5)
#
#				# vertical flow
#				if widget_flow_info["flow_type"] == "Vertical Flow":
#					point0 = Vector2(flow_middle_line[i], flow_end1[i])
#					point1 = Vector2(flow_middle_line[i], flow_end2[i])
#					point2 = Vector2(flow_middle_line[i] + 5, flow_end2[i] - 15)
#					point3 = Vector2(flow_middle_line[i] - 5, flow_end2[i] - 15)
#
#				# update the existing arrow lines
#				if i < current_num_lines:
#					$Globals.line_list[flow_name][i].set_point_position(0, point0)
#					$Globals.line_list[flow_name][i].set_point_position(1, point1)
#					$Globals.line_list[flow_name][i].set_point_position(2, point2)
#					$Globals.line_list[flow_name][i].set_point_position(3, point3)
#					$Globals.line_list[flow_name][i].set_point_position(4, point1)
#					$Globals.line_list[flow_name][i].visible = true
#
#				# create new arrow lines
#				else:
#					var line = Line2D.new()
#					print(line.get_default_color())
#
#					# set colors
#					var line_color
#					if widget_flow_info["flow_type"] == "Horizontal Flow":
#						line_color = Color( 0.4, 0.6, 1, 1 )		# blue
#					elif widget_flow_info["flow_type"] == "Vertical Flow":
#						line_color = Color( 0.4, 0.85, 0.5, 1 )		# green
#
#					# create arrow lines
#					line.set_width(5)
#					line.set_default_color(line_color)
#					root.add_child(line)
#					line.set_owner(root)
#					line.add_point(point0)
#					line.add_point(point1)
#					line.add_point(point2)
#					line.add_point(point3)
#					line.add_point(point1)
#					$Globals.line_list[flow_name].append(line)
#
#				# update dotted lines
#				if i < len(flow_end1) - 1:
#					var point_dot
#
#					# horizontal flow
#					if widget_flow_info["flow_type"] == "Horizontal Flow":
#						point_dot = Vector2(flow_end1[i+1], flow_middle_line[i+1])
#
#					# vertical flow
#					elif widget_flow_info["flow_type"] == "Vertical Flow":
#						point_dot = Vector2(flow_middle_line[i+1], flow_end1[i+1])
#
#					# update the existing dotted lines
#					if i < current_num_lines - 1:
#						$Globals.dotted_line_list[flow_name][i].set_point_position(0, point1)
#						$Globals.dotted_line_list[flow_name][i].set_point_position(1, point_dot)
#						$Globals.dotted_line_list[flow_name][i].visible = true
#
#					# create new dotted lines
#					else:
#						var line = Line2D.new()
#
#							# set colors
#						var line_color
#						if widget_flow_info["flow_type"] == "Horizontal Flow":
#							line_color = Color( 0.4, 0.6, 1, 0.3)		# blue
#						elif widget_flow_info["flow_type"] == "Vertical Flow":
#							line_color = Color( 0.4, 0.85, 0.5, 0.3 )		# green
#
#						# create dotted lines
#						root.add_child(line)
#						line.set_owner(root)
#						line.add_point(point1)
#						line.add_point(point_dot)
#						line.set_default_color(line_color)
#						$Globals.dotted_line_list[flow_name].append(line)
#
#			# make all the unused lines invisible
#			for i in range(len(flow_end1), current_num_lines):
#				$Globals.line_list[flow_name][i].visible = false
#			for i in range(len(flow_end1) - 1, current_num_lines - 1):
#				$Globals.dotted_line_list[flow_name][i].visible = false


func _on_visualize_constraints():
	
	# set visualization variables
#	$Globals.flow_visualization = false
	$Globals.constraint_visualization = true
	
	# get the layout root
	var root = get_tree().get_edited_scene_root()
	
	# get widget info including flow_elements, flow type, etc.
	var widget_info = json_helper.load_json("./widget_info.json")
	
	# load the produced result from ORCSolver
	# e.g., Text:{height:481, width:372, x:80, y:160}, 
	# VF:{height:481, width:80, x:0, y:160}, window_height:641, window_width:452}
	var updated_layout_info = json_helper.load_json("./initialization_inference.json")
	
	$Globals.vis_constraint_lines = []
	var current_num_lines = len($Globals.vis_constraint_lines)
#	return
	# visualize all the flows
	var used_widgets = []
	for child in root.get_children():
		var widget_id = child.get_name()
		
		############
		$Globals.vis_optional_widgets = []
		if widget_id == "5":
			var x = updated_layout_info[widget_id]["x"] 
			var y = updated_layout_info[widget_id]["y"] 
			var width = updated_layout_info[widget_id]["width"] 
			var height = updated_layout_info[widget_id]["height"] 
			var line = Line2D.new()
					
			# set colors
			var line_color = Color(0.7, 0.7, 0.2)

			# create arrow lines
			line.set_width(3)
			line.set_default_color(line_color)
			root.add_child(line)
			line.set_owner(root)
			line.add_point( Vector2(x + 10, y + 10) ) 
			line.add_point( Vector2(x + 5, y + 20) )
			line.add_point( Vector2(x + 15, y + 20) )
			line.add_point( Vector2(x + 10, y + 10) ) 
			$Globals.vis_optional_widgets.append(line)

		############
		
		# skip optional widgets
		if not (widget_id in widget_info):
			continue
			
		# get all the flow information
		var widget_flow_info = widget_info[widget_id]
		if not used_widgets.has(widget_id):

			# record all the used elements
			for id in widget_flow_info["flow_elements"]:
				used_widgets.append(id)
				
			# skip non flow elements
			if not "flow_name" in widget_flow_info:
				continue

			# get the flow name
			var flow_name = widget_flow_info["flow_name"]
				
			# get the line points for the lines and dotted lines
			var flow_end1 = [] 
			var flow_end2 = []
			var flow_begin_point = []
			var flow_end_line = []
			var end1 = 1000000
			var end2 = 1000000
			var num = 0
			for id in widget_flow_info["flow_elements"]:
				
				# skip optional widgets
				if root.find_node(id).rect_position.x == -1000:
					continue
					
				# compute the left, right and positon of the lines
				var x = updated_layout_info[id]["x"] 
				var y = updated_layout_info[id]["y"] 
				var width = updated_layout_info[id]["width"] 
				var height = updated_layout_info[id]["height"] 
				
				# horizontal flow
				if widget_flow_info["flow_type"] == "Horizontal Flow":
					if x + 5 < end2:
						end1 = x
						flow_end1.append(end1)
						end2 = x + width
						flow_end2.append(end2)
						flow_end_line.append(y + height)
						flow_begin_point.append(y)
					else:
						end2 = x + width
						flow_end2[-1] = end2
						flow_end_line[-1] = max(y + height, flow_end_line[-1])
						flow_begin_point[-1] = min(y, flow_begin_point[-1])
				
				# vertical flow
				elif widget_flow_info["flow_type"] == "Vertical Flow":
					if y + 5 < end2:
						end1 = y
						flow_end1.append(end1)
						end2 = y + height
						flow_end2.append(end2)
						flow_end_line.append(x + width)
						flow_begin_point.append(x)
					else:
						end2 = y + height
						flow_end2[-1] = end2
						flow_end_line[-1] = max(x + width, flow_end_line[-1])
						flow_begin_point[-1] = min(x, flow_begin_point[-1])

			# update arrow lines and dotted lines 
			for i in len(flow_end1):
				var point0
				var point1
				var point2
				
				# update arrow lines 
				# horizontal flow
				if widget_flow_info["flow_type"] == "Horizontal Flow":
					point0 = Vector2(flow_end1[i], flow_end_line[i])
					point1 = Vector2(flow_end2[i], flow_end_line[i])
					point2 = Vector2(flow_end2[i], flow_begin_point[i])
					
				# vertical flow
				elif widget_flow_info["flow_type"] == "Vertical Flow":
					point0 = Vector2(flow_end_line[i], flow_end1[i])
					point1 = Vector2(flow_end_line[i], flow_end2[i])
					point2 = Vector2(flow_begin_point[i], flow_end2[i])
				
				# update the existing arrow lines
				if i < current_num_lines:
					$Globals.vis_constraint_lines[i].set_point_position(0, point0)
					$Globals.vis_constraint_lines[i].set_point_position(1, point1)
					$Globals.vis_constraint_lines[i].set_point_position(2, point2)
					$Globals.vis_constraint_lines[i].visible = true
					
				# create new lines
				else:
					var line = Line2D.new()
					
					# set colors
					var line_color = Color(0.7, 0.7, 0.2)

					# create arrow lines
					line.set_width(8)
					line.set_default_color(line_color)
					root.add_child(line)
					line.set_owner(root)
					line.add_point(point0)
					line.add_point(point1)
					line.add_point(point2)
					$Globals.vis_constraint_lines.append(line)
					
			# make all the unused lines invisible
			for i in range(len(flow_end1), current_num_lines):
				$Globals.vis_constraint_lines[i].visible = false



func _on_remove_visualization():
	
	# set visualization variables
	$Globals.flow_visualization = false
	$Globals.constraint_visualization = false
	
	# get the layout root
	var root = get_tree().get_edited_scene_root()
	
	# set all the lines invisible
	for child in root.get_children():
		if child.get_class() ==  "Line2D":
			child.visible = false
