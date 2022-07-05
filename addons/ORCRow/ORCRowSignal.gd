tool
extends Container
export var flow_enabled = true
class_name ORCRow


func _enter_tree():
	connect("sort_children", self, "place_widgets")


func place_widgets():

	# get container position and size
	var container_x = self.rect_position.x
	var container_y = self.rect_position.y
	var container_width = self.rect_size.x
	
	# load the produced result from ORCSolver
	var json_helper = preload("res://addons/orc_editor/json_helper.gd")
	var updated_layout_info = json_helper.load_json("./initialization_inference.json") ####
	
	print(updated_layout_info)
	
	# move elements into the orc structure
#	var line = Node.new()
#	self.add_child(line)
#	line.set_owner(self)
	
	######
#	var w = $Globals.temp_number
#	var h = 50
#	print(self.name)
#	self.rect_position.x = updated_layout_info["HF"]["x"]
#	self.rect_position.y = updated_layout_info["HF"]["y"]
#	self.rect_size.x = updated_layout_info["HF"]["width"]
#	self.rect_size.y = updated_layout_info["HF"]["height"]

#	var w = 85
#	var h = 80
	#print($Globals.flow_enabled)
	#if $Globals.flow_enabled:
	if flow_enabled:
#		var x_pos = 0
#		var y_pos = 0
		for c in get_children():
			var widget_name = c.get_name()
			print(widget_name)
			if updated_layout_info.has(widget_name):
				c.rect_position.x = updated_layout_info[widget_name]["x"] - container_x
				c.rect_position.y = updated_layout_info[widget_name]["y"] - container_y
				c.rect_size.x = updated_layout_info[widget_name]["width"] 
				c.rect_size.y = updated_layout_info[widget_name]["height"] 

		
		
#	$Globals.line_list.append(line)
#	$Globals.line_list =  []
#	$Globals.line_list.visible = false

#	else:
#		var x_pos = 0
#		var y_pos = 0
#		for c in get_children():
#			c.rect_position.x = x_pos
#			c.rect_position.y = y_pos
#			c.rect_size.x = w
#			c.rect_size.y = h
#			x_pos += w

		
		
		
		
	
		# Fit to own size
		#fit_child_in_rect( c, Rect2( Vector2(), rect_size ) )
	
