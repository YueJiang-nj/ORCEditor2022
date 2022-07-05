#
# This file constructs a tree in json format to 
# describe the layout using Row and Column
#

from topological_equivalence_check import \
            Layout, Widget, tabstop_creation
import copy

ERROR_THRESHOD = 5

# get all the tabstops that divide 
# the sublayout into two parts 
# for horizontal tabstops, min=top, max=bottom
# for vetical tabstops, min=left, max=right
def get_tabstop_divider(tab, widgets, x_or_y):

    # get all the tabstops that divide 
    # the sublayout into two parts 
    tab_values = sorted(tab.keys())
    divide_layout_tabs = []
    for i in range(1, len(tab_values) - 1):
        tab_value = tab_values[i]

        # we check whether no widgets going across 
        # the current tabstop
        divide_layout = True

        # a tabstop is valid if widgets exist on both sides
        # smaller means left side for vertical tabstops
        # and top side for horizontal tabstops
        tabstop_smaller = False
        tabstop_larger = False

        for w in widgets:

            # for horizontal tabstops, min=top, max=bottom
            # for vetical tabstops, min=left, max=right
            if x_or_y == "y":
                min_boundary = w.top
                max_boundary = w.bottom
            elif x_or_y == "x":
                min_boundary = w.left
                max_boundary = w.right
            if min_boundary < tab_value - ERROR_THRESHOD \
                and max_boundary > tab_value + ERROR_THRESHOD:
                divide_layout = False

            # we say the tabstop divides the layout only if 
            # there is some element between it and the previous
            # tabstop that divides the layout
            elif max_boundary <= tab_value + ERROR_THRESHOD \
                    and (len(divide_layout_tabs) == 0 or 
                        not max_boundary <= divide_layout_tabs[-1] + ERROR_THRESHOD):
                tabstop_smaller = True
            elif min_boundary >= tab_value - ERROR_THRESHOD:
                tabstop_larger = True

        # a tabstop is valid if widgets exist on both side
        # so it is not valid if any side is empty
        if not tabstop_smaller or not tabstop_larger:
            divide_layout = False

        # remove tabstops if they are close to another one
        for other_tab in divide_layout_tabs:
            if abs(tab_value - other_tab) < ERROR_THRESHOD:
                divide_layout = False

        # if the current tabstop divides the layout
        # then save it to the lists
        if divide_layout:
            divide_layout_tabs.append(tab_value)

    return divide_layout_tabs


# find tabstop dividers for the layout
def find_tabstop_dividers(divide_layout_tabs, sublayout, \
                            x_or_y):
    # initialize tree structure for the layout
    tree_structure = {}

    # check the sublayout type
    if x_or_y == "y":
        Column_or_Row = "Column"
    elif x_or_y == "x":
        Column_or_Row = "Row"    

    # if we find tabstop dividers for the layout,
    # we know it is a Column sublayout for y-tabstops,
    # it is a Row sublayout for x-tabstops
    if x_or_y == "y":
        remaining_widgets = sorted(sublayout.widgets, key=lambda w: w.bottom)
    if x_or_y == "x":
        remaining_widgets = sorted(sublayout.widgets, key=lambda w: w.right)
    tree_structure[Column_or_Row] = []

    sublayout_widgets_list = [] ####### change to obj

    # for each tabstop divider, we get the widgets
    # between it and its previous divider and put
    # these widgets into a new sublayout
    for tab_value in divide_layout_tabs:
        sublayout_widgets = []
        sublayout_left = None
        sublayout_right = None
        sublayout_top = None
        sublayout_bottom = None
        for w in remaining_widgets.copy():
            if x_or_y == "y":
                sort_key = w.bottom
            elif x_or_y == "x":
                sort_key = w.right
            if sort_key <= tab_value + ERROR_THRESHOD:
                sublayout_widgets.append(w)
                remaining_widgets.remove(w)
                if sublayout_left == None:
                    sublayout_left = w.left
                    sublayout_right = w.right
                    sublayout_top = w.top
                    sublayout_bottom = w.bottom
                else:
                    sublayout_left = min(sublayout_left, w.left)
                    sublayout_right = max(sublayout_right, w.right)
                    sublayout_top = min(sublayout_top, w.top)
                    sublayout_bottom = max(sublayout_bottom, w.bottom)
        
        # if no widgets between two tabstops, we ignore one tabstop
        if sublayout_left == None:
            continue

        # create new sublayout according to the tabstop
        tree_structure[Column_or_Row].append(construct_layout_tree(Layout( \
                                sublayout_widgets, \
                                sublayout_left, sublayout_right, \
                                sublayout_top, sublayout_bottom)))
        sublayout_widgets_list.append(sublayout_widgets)
    
    # if no widgets between two tabstops, we ignore one tabstop
    if len(remaining_widgets) != 0:

        # add the remaining widgets that are the widgets after 
        # the last tabstop divider
        if x_or_y == "y":
            tree_structure[Column_or_Row].append(construct_layout_tree(Layout(\
                                        remaining_widgets, \
                                        sublayout.left, sublayout.right, \
                                        tab_value, sublayout.bottom)))
        if x_or_y == "x":
            tree_structure[Column_or_Row].append(construct_layout_tree(Layout(\
                                        remaining_widgets, \
                                        tab_value, sublayout.right, \
                                        sublayout.top, sublayout.bottom)))
        sublayout_widgets_list.append(remaining_widgets)

    # recursively simplify the tree structure
    simplification_list = []
    structure_list = tree_structure[Column_or_Row]

    # check each element in the list, if there are 
    # consecutive non-int elements, then rerun the 
    # algorithm to simplify the result
    i = 0
    simplified_part = []
    while i < len(structure_list):
        # if type(structure_list[i]) != int:
        for k in range(i, len(structure_list)):
            if type(structure_list[k]) == int:
                break
        if i == k - 1 or i == k:
            i += 1
            continue

        # we try simplifying the sublayout until find a 
        # largest simplified version
        simplified = False 
        while k > i + 1 and simplified == False:
            widgets = []
            for j in range(i, k):
                widgets += sublayout_widgets_list[j]
            new_structure = construct_layout_tree(Layout(\
                    widgets, \
                    sublayout.left, sublayout.right, \
                    sublayout.top, sublayout.bottom))

            # if we find a simplifed version for the sublayout
            # then replace the original version with the 
            # simplified version
            # the simplified_part is a list containing the index
            # range of the original version which needs to be
            # replaced and the simplified version
            if tree_structure[Column_or_Row][i:k] != new_structure \
                and list(new_structure.keys())[0] != Column_or_Row:
                simplified = True
                simplified_part.append([i, k, new_structure])
            k -= 1
        i = k + 1


    # simplify the tree structure
    for i, k, new_structure in simplified_part[::-1]:
        tree_structure[Column_or_Row] \
            = tree_structure[Column_or_Row][:i] \
                + tree_structure[Column_or_Row][k:]
        tree_structure[Column_or_Row].insert(i, new_structure)

    # we return Column once we find the tabstop dividers
    return tree_structure


# recursively construct rows and cols
# tree_structure contains all the rows and columns
def construct_layout_tree(sublayout):

    # create tabstops mapping from tabstop values
    # to tabstops
    xtab, ytab = tabstop_creation(sublayout)

    # get the all widgets in the layout
    widgets = sublayout.widgets

    # ######### change id to widgets
    if len(widgets) == 1:
        return widgets[0].id

    # if no horizontal dividers, we check vertical ones
    # get all the x-tabstops (horizontal tabstops) that 
    # divides the sublayout into two parts 
    divide_layout_xtabs = get_tabstop_divider(xtab, widgets, "x")

    # get all the y-tabstops (horizontal tabstops) that 
    # divides the sublayout into two parts 
    divide_layout_ytabs = get_tabstop_divider(ytab, widgets, "y")

    print("====", xtab.keys(), ytab.keys(), divide_layout_xtabs, divide_layout_ytabs)

    # if we find horizontal tabstop dividers for the layout,
    # and there are more horizontal dividers than vertical
    # ones or we do not find any vertical dividers
    # we know it is a Column sublayouts
    if len(divide_layout_ytabs) > 0 \
        and (len(divide_layout_ytabs) <= len(divide_layout_xtabs) \
            or len(divide_layout_xtabs) == 0):
        return find_tabstop_dividers(divide_layout_ytabs, \
                                        sublayout, "y")

    # if we find vertical tabstop dividers for the layout,
    # we know it is a Row sublayouts
    if len(divide_layout_xtabs) > 0:
        return find_tabstop_dividers(divide_layout_xtabs, \
                                        sublayout, "x")

    ####### other pinwheel layout
    return #construct_row_col(new_layout, tree_structure, unique_id + 1)



