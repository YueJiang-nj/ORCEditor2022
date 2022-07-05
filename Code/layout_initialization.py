from flow_solver import *
from orclayout_classes import *
from construct_layout_tree import *
from tree_diff import *
from orc_pattern_recognition import *
import time


# the maximum difference for a flow
ERROR_THRESHOLD = 10 

# the minimum number of individual widgets as a flow
NUM_WIDGET_THRESHOLD = 3

# given the element list of the potential horizontal/vertical flow, 
# identify flows and compute the height/width of each row/column 
# structure_json: include structure_type and element_list,
#                   e.g., {"Row": [1,2,3]}
# structure_type: "Row" or "Column"
# element_list: the element list in the structure
#               each element is either a widget or a structure
# widget_dict: widget id to widget mapping
# return ORCLayout, sublayout size is a dict with keys width, height
def get_orclayout_structure(structure_json, widget_dict, 
                            orcwidget_list, root=False):

    # get structure type Row or Column and the element list
    structure_type = list(structure_json.keys())[0]
    element_list = structure_json[structure_type]

    # store the height and width of each element
    sublayout_height_list = []
    sublayout_width_list = []

    # sublayout list in the structure
    sublayout_list = []

    # count the number of individual widgets
    # Note: we only think a structure is a flow if it 
    #       contains at least 3 individual widgets
    num_widgets = 0 

    # store the list of width and height lists 
    # of sublayouts
    subsublayout_width_list_collection = []
    subsublayout_height_list_collection = []

    # loop over element list
    for element in element_list:

        # when the element is a widget
        if type(element) != type(dict()):
            widget = widget_dict[element]
            sublayout_height = widget.bottom - widget.top
            sublayout_width = widget.right - widget.left
            # sublayout = ORCWidget(element, \
            #           [70, sublayout_width,
            #            90, 70, \
            #            sublayout_height, 90])
            # sublayout = ORCWidget(element, \
            #           [80, sublayout_width, 80,  
            #            80, sublayout_height,80])
            if element == "Text": ######### TODO should be if it is not button
                sublayout = ORCWidget(element, \
                      [0, sublayout_width, 100000,  
                       0, sublayout_height,100000])
            else:
                sublayout = ORCWidget(element, \
                      [sublayout_width, sublayout_width,sublayout_width,
                      sublayout_height,sublayout_height,sublayout_height])
            # else:
            #     sublayout = ORCWidget(element, \
            #           [0, 100,100000,0,100,100000])
            #     sublayout.set_weight(0.00001)
            # print("ORCWidget", element)
            # if len(element) == 1:
            #     sublayout = ORCWidget(element, \
            #           [80, sublayout_width, 80,  
            #            80, sublayout_height,80])
            
            
            orcwidget_list[element] = sublayout
            num_widgets += 1
            subsublayout_width_list_collection.append([sublayout_width])
            subsublayout_height_list_collection.append([sublayout_height])

        # when the element is a sublayout
        else:
            sublayout, sublayout_size, subsublayout_width_list, \
                subsublayout_height_list = get_orclayout_structure(
                                            element, widget_dict, orcwidget_list)
            sublayout_height = sublayout_size["height"]
            sublayout_width = sublayout_size["width"]
            subsublayout_width_list_collection.append(subsublayout_width_list)
            subsublayout_height_list_collection.append(subsublayout_height_list)

        # add height, width, sublayout to the lists
        sublayout_height_list.append(sublayout_height)
        sublayout_width_list.append(sublayout_width)
        sublayout_list.append(sublayout)

    # deal with the case when the structure type is Row
    if structure_type == "Row":

        # if it is a flow then it is a horzontal flow
        if max(sublayout_height_list) \
            - min(sublayout_height_list) < ERROR_THRESHOLD \
            and num_widgets >= NUM_WIDGET_THRESHOLD \
            and not root: 
            ORCLayout_structure = HorizontalFlow("HF", sublayout_list)
            print("HorizontalFlow", len(sublayout_list))

        # otherwise it is a normal row
        else:
            ORCLayout_structure = ORCRow("Row")
            print("Row")

            # set root if it is the root
            if root == True:
                ORCLayout_structure.root = True

            # combine proper vertical flows
            i = 0
            while i < len(sublayout_list):
                end_i = i + 1
                if isinstance(sublayout_list[i], VerticalFlow):
                    flow_widget_list = sublayout_list[i].widget_list[:]

                    flow_subsublayout_width_list = subsublayout_width_list_collection[i][:]
                    new_sublayout = None

                    # sublayouts are only possible to be combined if they are flows
                    # or flows followed by a widget 
                    while end_i < len(sublayout_list) \
                        and (isinstance(sublayout_list[end_i], ORCWidget) \
                            or isinstance(sublayout_list[end_i], VerticalFlow)):
                        if isinstance(sublayout_list[end_i], VerticalFlow):
                            flow_widget_list += sublayout_list[end_i].widget_list
                        elif isinstance(sublayout_list[end_i], ORCWidget):
                            flow_widget_list += [sublayout_list[end_i]]
                        flow_subsublayout_width_list \
                                    += subsublayout_width_list_collection[end_i]

                        # check whether the flows can be combined
                        if max(flow_subsublayout_width_list) \
                            - min(flow_subsublayout_width_list) < ERROR_THRESHOLD:
                            new_sublayout = VerticalFlow("VF", flow_widget_list)
                            print("VerticalFlow", len(flow_widget_list))
                            end_i += 1
                        else:
                            break

                    # if flows are combined, then we put new flows to the list
                    if new_sublayout:
                        sublayout_list = sublayout_list[:i] + [new_sublayout] \
                                                + sublayout_list[end_i:]
                i = end_i

            # set sublayout list for the Row
            ORCLayout_structure.define_sublayouts(sublayout_list)
            print("define_sublayouts", type(ORCLayout_structure), sublayout_list)

            # set parents for structures inversely
            for i in range(len(sublayout_list) - 1, 0, -1):
                sublayout_list[i].set_parent(sublayout_list[i-1])
                print("set_parent", type(sublayout_list[i]), type(sublayout_list[i-1]))
            sublayout_list[0].set_parent(ORCLayout_structure)
            print("set_parent", type(sublayout_list[0]), type(ORCLayout_structure))


        # the structure width is the sum of all the sublayouts
        # and the height is the average sublayout height
        structure_size = {"width": sum(sublayout_width_list),
            "height": sum(sublayout_height_list) / len(sublayout_height_list)}

    # deal with the case when the structure type is Column
    elif structure_type == "Column":

        # if it is a flow then it is a vertical flow
        if max(sublayout_width_list) \
            - min(sublayout_width_list) < ERROR_THRESHOLD \
            and num_widgets >= NUM_WIDGET_THRESHOLD \
            and not root: 
            ORCLayout_structure = VerticalFlow("VF", sublayout_list)
            print("VerticalFlow", len(sublayout_list))

        # otherwise it is a normal row
        else:
            ORCLayout_structure = ORCColumn("Column")
            print("Column")

            # set root if it is the root
            if root == True:
                ORCLayout_structure.root = True

            
            # combine proper horizontal flows
            i = 0
            while i < len(sublayout_list):
                end_i = i + 1
                if isinstance(sublayout_list[i], HorizontalFlow):
                    flow_widget_list = sublayout_list[i].widget_list[:]
                    flow_subsublayout_height_list = subsublayout_height_list_collection[i][:]
                    new_sublayout = None

                    # sublayouts are only possible to be combined if they are flows
                    # or flows followed by a widget 
                    while end_i < len(sublayout_list) \
                         and (isinstance(sublayout_list[end_i], ORCWidget) \
                            or isinstance(sublayout_list[end_i], HorizontalFlow)):  
                        if isinstance(sublayout_list[end_i], HorizontalFlow):
                            flow_widget_list += sublayout_list[end_i].widget_list
                        elif isinstance(sublayout_list[end_i], ORCWidget):
                            flow_widget_list += [sublayout_list[end_i]]
                        flow_subsublayout_height_list \
                                    += subsublayout_height_list_collection[end_i]

                        # check whether the flows can be combined
                        if max(flow_subsublayout_height_list) \
                            - min(flow_subsublayout_height_list) < ERROR_THRESHOLD:
                            new_sublayout = HorizontalFlow("HF", flow_widget_list)
                            print("HorizontalFlow", flow_widget_list)
                            end_i += 1
                        else:
                            break

                    # if flows are combined, then we put new flows to the list
                    if new_sublayout:
                        sublayout_list = sublayout_list[:i] + [new_sublayout] \
                                                + sublayout_list[end_i:]
                i = end_i
            ORCLayout_structure.define_sublayouts(sublayout_list)
            print("define_sublayouts", type(ORCLayout_structure), sublayout_list)

            # set parents for structures inversely
            for i in range(len(sublayout_list) - 1, 0, -1):
                sublayout_list[i].set_parent(sublayout_list[i-1])
                print("set_parent", type(sublayout_list[i]), type(sublayout_list[i-1]))
            sublayout_list[0].set_parent(ORCLayout_structure)
            print("set_parent", type(sublayout_list[0]), type(ORCLayout_structure))

        # the structure height is the sum of all the sublayouts
        # and the width is the average sublayout width
        structure_size = {"height": sum(sublayout_height_list),
            "width": sum(sublayout_width_list) / len(sublayout_width_list)}

    return ORCLayout_structure, structure_size, \
            sublayout_width_list, sublayout_height_list



    





