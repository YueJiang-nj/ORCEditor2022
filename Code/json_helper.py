import json


def load_json(path):
	""" 
	Load a json file.
	"""

	# open a json file
	with open(path) as json_file:
		content = json.load(json_file)

	return content


def write_json(content, path):
	""" 
	Write the content to a json file.
	"""

	# open a json file
	with open(path, "w") as json_file:
		json.dump(content, json_file)
