tool
extends Container
export var flow_enabled = true
class_name ORCColumn

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

	

	if flow_enabled:
		for c in get_children():
			var widget_name = c.get_name()
			print(widget_name)
			if updated_layout_info.has(widget_name):
				c.rect_position.x = updated_layout_info[widget_name]["x"] - container_x
				c.rect_position.y = updated_layout_info[widget_name]["y"] - container_y
				c.rect_size.x = updated_layout_info[widget_name]["width"] 
				c.rect_size.y = updated_layout_info[widget_name]["height"] 
	
