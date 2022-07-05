tool
extends EditorPlugin


# A class member to hold the dock during the plugin life cycle.
var dock 
var current_selected_object 
var scene_root = get_tree().get_edited_scene_root()

func _enter_tree():
	# Initialization of the plugin goes here.
	# Load the dock scene and instance it.
	dock = preload("res://addons/orc_editor/orc_editor.tscn").instance()

	# Add the loaded scene to the docks.
	add_control_to_dock(DOCK_SLOT_RIGHT_BL, dock)
	# Note that LEFT_UL means the left of the editor, upper-left dock.
	
	connect("scene_changed", dock, "_on_scene_changed")
	
func handles(object):
	current_selected_object = object
	return true 

func forward_canvas_gui_input(event):
	var scene_root = get_tree().get_edited_scene_root()
	var dock = preload("res://addons/orc_editor/orc_editor.tscn").instance()

#	if event is InputEventMouseButton:
#
#		if event.doubleclick:
#			scene_root.get_node("PopupDialog").visible = true
#			var theme = load("res://addons/orc_editor/normal_theme.tres")
#
#			if current_selected_object.get_name() == "yes":
#				scene_root.get_node("PopupDialog").rect_position.x = -1000
#				scene_root.get_node("PopupDialog").rect_position.y = -1000
#				var temp = scene_root.get_node("7").rect_position
#				scene_root.get_node("7").rect_position = scene_root.get_node("6").rect_position 
#				scene_root.get_node("6").rect_position = temp
#				scene_root.get_node("7").set_theme(theme)
#				scene_root.get_node("6").set_theme(theme)
#				dock.get_node("Globals").widget_error_message["6"] = ":"
#				dock.get_node("Globals").widget_error_message["7"] = ":"
#
#			else:
#	#			var scene_root = get_tree().get_edited_scene_root()
#				var widget_id = current_selected_object.get_name()
#				scene_root.get_node("PopupDialog").rect_position.x \
#										= current_selected_object.rect_position.x
#				scene_root.get_node("PopupDialog").rect_position.y \
#									= current_selected_object.rect_position.y \
#										+ current_selected_object.rect_size.y
#				var message = dock.get_node("Globals").widget_message[widget_id]
#				var error_message = dock.get_node("Globals").widget_error_message[widget_id]
#				if error_message[-1] == ":":
#					scene_root.get_node("PopupDialog/info").set_text(message)
#					scene_root.get_node("PopupDialog/error").set_text("")
#					scene_root.get_node("PopupDialog/yes").visible = false
#					scene_root.get_node("PopupDialog/no").visible = false
#				else:
#					scene_root.get_node("PopupDialog/error").set_text(error_message)
#					scene_root.get_node("PopupDialog/info").set_text("")
#					scene_root.get_node("PopupDialog/yes").visible = true
#					scene_root.get_node("PopupDialog/no").visible = true
					

#			scene_root.get_node("PopupDialog").set('z_index', 0)
#			print(editor.get_node("Globals").view_list)
#			scene_root.get_node("Label").set_text("aaaaa")
#		else:
##			yield(get_tree().create_timer(5), "timeout")
#			scene_root.get_node("PopupDialog").rect_position.x \
#									= -1000
#			scene_root.get_node("PopupDialog").rect_position.y \
#							= -1000
			
	return false
	


func _exit_tree():
	# Clean-up of the plugin goes here.
	# Remove the dock.
	remove_control_from_docks(dock)
	# Erase the control from the memory.
	dock.free()
