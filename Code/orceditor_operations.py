from flow_solver import *
from orclayout_classes import *
import time
from random import randint
from json_helper import *
from construct_layout_tree import *
from tree_diff import *
from orc_pattern_recognition import *
from layout_initialization import *
import time
import sys, os
import pickle
import itertools


# get layout info from a json file
def get_layout_info_from_json(json):

    # load layout info
    layout_info = load_json(json)
    window_width = round(layout_info["root"]["width"])
    window_height = round(layout_info["root"]["height"])

    # store layout info
    layout = Layout([], 0, window_width, 0, window_height)
    for key in layout_info.keys():
        if key != "root":
            x = round(layout_info[key]["x"])
            y = round(layout_info[key]["y"])
            width = round(layout_info[key]["width"])
            height = round(layout_info[key]["height"])
            widget = Widget(key, x, x + width, y, y + height)
            layout.add_widget(widget)
    return layout

# save widget info regarding flows
def save_widget_info(ORCLayout_structure):

    # save widget info 
    widget_info = dict()
    for widget_id in ORCLayout_structure.orcwidgets.keys():
        widget = ORCLayout_structure.orcwidgets[widget_id]
        widget_info[widget_id] = dict()
        widget_info[widget_id]["flow_type"] = ""
        widget_info[widget_id]["flow_elements"] = []
        widget_info[widget_id]["optional_elements"] = []
        if isinstance(widget.flow_parent, HorizontalFlow) == True:
            widget_info[widget_id]["flow_type"] = "Horizontal Flow"
            widget_info[widget_id]["flow_name"] = widget.flow_parent.name
            for flow_element in widget.flow_parent.widget_list:
                widget_info[widget_id]["flow_elements"].append(flow_element.name)
                if flow_element.optional:
                    widget_info[widget_id]["optional_elements"].append(flow_element.name)
        elif isinstance(widget.flow_parent, VerticalFlow) == True:
            widget_info[widget_id]["flow_type"] = "Vertical Flow"
            widget_info[widget_id]["flow_name"] = widget.flow_parent.name
            for flow_element in widget.flow_parent.widget_list:
                widget_info[widget_id]["flow_elements"].append(flow_element.name)
                if flow_element.optional:
                    widget_info[widget_id]["optional_elements"].append(flow_element.name)
    write_json(widget_info, "./widget_info.json")

# get first view information and infer orclayout structure 
def initialization(json, window_width, window_height):

    # load layout info
    layout = get_layout_info_from_json(json)

    # get the layout tree structure
    tree_json = construct_layout_tree(layout)

    # get the mapping from widget id to the corresponding weight
    widget_dict = layout.widget_dict

    # store orcwidget list for later defining optional widgets
    orcwidget_list = dict()

    # detect flows in the tree
    ORCLayout_structure, _, _, _ = get_orclayout_structure(
                tree_json, widget_dict, orcwidget_list, root=True)
    ORCLayout_structure.orcwidgets = orcwidget_list

    # save optional, misordered, mispositioned elements
    with open("./element_diff/optional_elements.txt", "w") as f:
        f.write("")
    with open("./element_diff/misordered_elements.txt", "w") as f:
        f.write("")
    with open("./element_diff/mispositioned_elements.txt", "w") as f:
        f.write("")

    # save widget info regarding flows
    save_widget_info(ORCLayout_structure)

    # open a pickle file
    filename = './orclayout_initialization.pk'

    # save ORCLayout structure
    with open(filename, 'wb') as file:

        # dump ORCLayout structure into the file
        pickle.dump(ORCLayout_structure, file)

    # update the current layout status for the initialization
    solve_orclayout_specification(window_width, window_height, 1)


# get all the sublists of the list
def get_sublist(lst):
    sublists = []
    for i in range(len(lst), 1, -1):
        sublists += itertools.combinations(lst, i)
    return sublists

# get longest common sublist between two lists
def get_longest_common_sublists(list1, list2):
    longest_common_sublists = []
    longest_length = len(list1)
    for sublist in get_sublist(list1):
        if sublist in get_sublist(list2):
            if longest_length == len(list1):
                longest_length = len(sublist)
            if longest_length == len(sublist):
                longest_common_sublists.append(sublist)
    return longest_common_sublists

# get misordered elements compared between two lists
def get_misordered_elements(list1, list2):
    misordered_element_list = set()
    longest_common_sublists = get_longest_common_sublists(list1, list2)
    for sublist in longest_common_sublists:
        misordered_element_list.update(set(list1) - set(sublist))
    return misordered_element_list

# update orclayout specification
def update_orclayout_specification(json_list):

    # load orclayout structure
    filename = './orclayout_initialization.pk'
    with open(filename, 'rb') as file:
        ORCLayout_structure = pickle.load(file)

    # get the list of json files
    json_list = json_list[1:-1].split(",")
    tree_json_list = []

    # get tree structure from json files
    for json in json_list:

        # get json path
        json_path = "./json_files/" + json.strip() + ".json"

        # load layout info
        layout = get_layout_info_from_json(json_path)

        # get the layout tree structure
        tree_json = construct_layout_tree(layout)
        tree_json_list.append(tree_json)

    # compute the layout differences
    misordered_elements = set()
    mispositioned_elements = set()
    optional_elements = set()
    first_view = tree_json_list[0]
    for i in range(1, len(tree_json_list)):
        changes = detect_tree_diff(first_view, tree_json_list[i])
        pattern_results = orc_pattern_recognition(changes)

        # update orclayout specification 
        ######## TODO: add other patterns
        for layout_diff in pattern_results:
            if layout_diff[0] == "Optional Wdiget":
                widget_id = layout_diff[1]
                ORCLayout_structure.orcwidgets[widget_id].set_optional()
                ORCLayout_structure.orcwidgets[widget_id].flow_parent.update_optional_widgets()
                optional_elements.add(widget_id)
            elif layout_diff[0] == "Change Children Order":
                from_ids = layout_diff[1]
                to_ids = layout_diff[2]
                misordered_elements = get_misordered_elements(from_ids, to_ids)
            elif layout_diff[0] == "Alternative Position":
                widget_id = layout_diff[1]
                mispositioned_elements.add(widget_id)

    # save optional, misordered, mispositioned elements
    with open("./element_diff/optional_elements.txt", "w") as f:
        for element in optional_elements:
            f.write(element + " ")
    with open("./element_diff/misordered_elements.txt", "w") as f:
        for element in misordered_elements:
            f.write(element + " ")
    with open("./element_diff/mispositioned_elements.txt", "w") as f:
        for element in mispositioned_elements:
            f.write(element + " ")

    # save widget info regarding flows
    save_widget_info(ORCLayout_structure)

    # open a pickle file
    filename = './orclayout_specification.pk'

    # save ORCLayout structure
    with open(filename, 'wb') as file:

        # dump ORCLayout structure into the file
        pickle.dump(ORCLayout_structure, file)


# get all the info for horizontal flows
def get_horizontal_flow_info(left_position, top_position, \
                            flow_row_height, flow_row_width, flow_result_index,
                            flow_widgets, layout_info):
    
    # get the corrct positions of widgets in the horizontal flow
    left = left_position
    top = top_position
    index = 0
    for i in range(len(flow_result_index)):
        for j in range(len(flow_result_index[i])):
            index = flow_result_index[i][j]
            widget_width = flow_row_width[i][j]
            widget_height = flow_row_height[i]
            widget_name = flow_widgets[index].name
            layout_info[widget_name] = dict()
            layout_info[widget_name]["x"] = round(left)
            layout_info[widget_name]["y"] = round(top)
            layout_info[widget_name]["width"] = round(widget_width)
            layout_info[widget_name]["height"] = round(widget_height)
            left += widget_width
            index += 1
        left = left_position
        top += widget_height


# get all the info for vertical flows
def get_vertical_flow_info(left_position, top_position, \
                            flow_row_height, flow_row_width, flow_result_index,
                            flow_widgets, layout_info):
    
    # get the corrct positions of widgets in the vertical flow
    left = left_position
    top = top_position
    for i in range(len(flow_result_index)):
        for j in range(len(flow_result_index[i])):
            index = flow_result_index[i][j]
            widget_width = flow_row_width[i]
            widget_height = flow_row_height[i][j]
            widget_name = flow_widgets[index].name
            layout_info[widget_name] = dict()
            layout_info[widget_name]["x"] = round(left)
            layout_info[widget_name]["y"] = round(top)
            layout_info[widget_name]["width"] = round(widget_width)
            layout_info[widget_name]["height"] = round(widget_height)
            top += widget_height
        left += widget_width
        top = top_position


# update the result according to new window size
def solve_orclayout_specification(window_width, window_height, initialization):

    # load orclayout structure
    if int(initialization) == 1:
        print("Layout Initialization...")
        filename = './orclayout_initialization.pk'
    else:
        filename = './orclayout_specification.pk'
    with open(filename, 'rb') as file:
        ORCLayout_structure = pickle.load(file)

    # set window width and height
    ORCLayout_structure.width = window_width
    ORCLayout_structure.height = window_height

    # solve orclayout structure with new window size
    ORCLayout_structure.solve()
    best_leaf, best_leaf_result, best_leaf_loss = ORCLayout_structure.get_best()
    print('+++++')
    print(best_leaf, best_leaf_result, best_leaf_loss)
    exit()

    # save all the widgets results
    layout_info = dict()
    layout_info["window_width"] = int(float(window_width))
    layout_info["window_height"] = int(float(window_height))
    for key in best_leaf_result.keys():

        # since keys are xxx_l, xxx_t, xxx_r, xxx_b
        if key[-2:] == "_l":
            element_name = key[:-2]
            top = best_leaf_result[element_name + "_t"]
            left = best_leaf_result[element_name + "_l"]
            bottom = best_leaf_result[element_name + "_b"]
            right = best_leaf_result[element_name + "_r"]
            layout_info[element_name] = dict()
            layout_info[element_name]["x"] = round(left)
            layout_info[element_name]["y"] = round(top)
            layout_info[element_name]["width"] = round(right) - round(left)
            layout_info[element_name]["height"] = round(bottom) - round(top)

    # get all the info for widgets in flows
    while best_leaf.parent != None:
        if isinstance(best_leaf, Flow):
            flow_name = best_leaf.name
            flow_row_height = best_leaf.best_row_height
            flow_row_width = best_leaf.best_row_width
            flow_result_index = best_leaf.best_result_index
            flow_widgets = best_leaf.widget_list

            # get the left top corner of the flow
            left_position = layout_info[flow_name]["x"]
            top_position = layout_info[flow_name]["y"]
            
            # get horizontal flow info
            if isinstance(best_leaf, HorizontalFlow):
                get_horizontal_flow_info(left_position, top_position, \
                            flow_row_height, flow_row_width, flow_result_index,
                            flow_widgets, layout_info)
            elif isinstance(best_leaf, VerticalFlow):
                get_vertical_flow_info(left_position, top_position, \
                            flow_row_height, flow_row_width, flow_result_index,
                            flow_widgets, layout_info)

        # move to the parent level
        best_leaf = best_leaf.parent

    # write update results
    write_json(layout_info, "./initialization_inference.json") ##





