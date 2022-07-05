extends Node


export var first_view_saved : bool = false
export var view_list := []
export var updated_layout_info_list := []
export var ready : bool = false
export var widget_message := {}
export var widget_error_message := {}
export var flow_enabled : bool = false
export var temp_number = 50
export var line_list = {}
export var dotted_line_list = {}
export var flow_visualization = false
export var constraint_visualization = false
export var vis_constraint_lines = []
export var vis_optional_widgets = []
export var vis_flow_trangles = {}
