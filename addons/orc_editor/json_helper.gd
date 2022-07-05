extends Control
tool


static func load_json(path):
	""" 
	Load a JSON file
	"""
	
	# open the JSON file
	var file = File.new()
	file.open(path, file.READ)
	
	# get the content of the JSON file
	var text = file.get_as_text()
	var json_result  = JSON.parse(text)
	file.close()
	
	# check whether the parse is valid and extract results
	if json_result.error == OK:
		var result = json_result.result
		return result
	else:
		print("ERROR: The JSON file cannot be parsed.")
		return


static func write_json(content, path):
	""" 
	Write into a JSON file
	"""
	
	# open a JSON file
	var file = File.new()
	if file.open(path, File.WRITE) != 0:
		print("ERROR: The JSON file cannot be created.")
		return
		
	# save the dictionary to the JSON file
	file.store_line(to_json(content))
	file.close()



