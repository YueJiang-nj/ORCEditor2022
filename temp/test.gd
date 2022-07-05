extends Control


# Called when the node enters the scene tree for the first time.
func _ready():
	$MenuButtonFile.get_popup().add_item("Open File")
	$MenuButtonFile.get_popup().add_item("Save File")
	$MenuButtonFile.get_popup().add_item("Quit")
	$MenuButtonFile.get_popup().connect("id_pressed", self, "_on_item_pressed")
	$MenuButtonHelp.get_popup().add_item("About")
	$MenuButtonHelp.get_popup().connect("id_pressed", self, "_on_item_help_pressed")
#	var root = get_tree().get_edited_scene_root()
	for b in self.get_children():
		print(b.get_name(), "yuyue")
		b.connect("gui_input", self, "_on_gui_input", [b])
#		b.connect("mouse_entered", self, "_on_gui_input", [b])
#		b.connect("focus_entered", self, "_on_gui_input", [b])
#		b.connect("resized", self, "_on_gui_input", [b])
	
#	func _ready():
	get_node("Button").connect("input_event", self, "on_input")
	
#var Mouse_Position
#func _process(delta):
#	Mouse_Position = get_local_mouse_position()
#	print(Mouse_Position)
	
func on_input(ev):
	if  ev.is_pressed():
		print("double clicked !")
	
func _on_item_pressed(id):
	var item_name = $MenuButtonFile.get_popup().get_item_text(id)
	if item_name == "Open File":
		$FileDialog.popup()
	elif item_name == "Save File":
		$SaveFileDialog.popup()
	elif item_name == "Quit":
		get_tree().quit()
	elif item_name == "About":
		$AboutDialog.popup()
	
	print(item_name)

func _on_item_help_pressed(id):

	var item_name = $MenuButtonHelp.get_popup().get_item_text(id)
	if item_name == "About":
		var theme = load("res://addons/orc_editor/red_color.tres")
		$Button.set_theme(theme)
		$AboutDialog.popup()
	


func _on_OpenFile_pressed():
	$FileDialog.popup()


func _on_SaveFile_pressed():
	$SaveFileDialog.popup()


func _on_FileDialog_file_selected(path):
	print(path)
	var f = File.new()
	f.open(path, 1)
	$TextEdit.text = f.get_as_text()
	f.close()


func _on_SaveFileDialog_file_selected(path):
	var f = File.new()
	f.open(path, 2)
	f.store_string(TextEdit.text)
	f.close()


func _on_gui_input(event, b):
#	print("-----", b)
	if event is InputEventMouseButton:
		if event.doubleclick:
			print("-----", b)
			$PopupDialog.rect_position.x = b.rect_position.x 
			$PopupDialog.rect_position.y = b.rect_position.y + b.rect_size.y
			$PopupDialog.popup()
#			print(b.get_name())
#		print("22222")


