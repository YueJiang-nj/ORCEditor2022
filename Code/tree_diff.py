#
# This file is used for comparing two trees
#

import hashlib

# integer and string hash function
def customized_hash(x):
    if type(x) == int:
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = (x >> 16) ^ x
        
    elif type(x) == str:
        x = int(hashlib.sha1(x.encode("utf-8")).hexdigest(), 16) % (10 ** 8)

    return x


# define tree node 
# note that widget_id must be int
class Node():
    def __init__(self, parent, widget_id, child_num):

        # widget id is "Row" or "Column" if it is 
        # an internal node
        self.widget_id = widget_id
        self.parent = parent

        # if it is a leaf node, we assign a hash code
        # based on our defined integer hash function
        if self.widget_id != "Row" and self.widget_id != "Column":
            self.hash_code = customized_hash(widget_id)
            self.childhash_code = self.hash_code

        # if it is not a leaf node, we assign a hash
        # code of python enbedded hash function
        # hash("Row") or hash("Column")
        else:
            self.hash_code = hash(widget_id)

            # childhash_code is 0 if no child 
            self.childhash_code = 0

        # it is the 1st/2nd/3rd/... child of parent
        if parent:
            self.path_to_root = parent.path_to_root \
                                + [(parent, child_num)]
        else:
            self.path_to_root = []
        self.children = []
        self.children_codes = []

        # if it is a leaf node, then the leaf set 
        # only contains itself
        if self.widget_id != "Row" and self.widget_id != "Column":
            self.leaves = [self.widget_id]

        # if it is a non-leaf node, then we 
        # add leaves when we add leaf node
        # in this subtree
        else:
            self.leaves = []

    def add_child(self, node):
        self.children.append(node)
        self.children_codes.append(node.hash_code)

        # hash code for a parent is defined as 
        # hash("Row"/"Column") + 1 * hash code of the 1st 
        # child node + 2 * hash code of the 2nd child node
        # + 3 * hash code of the 3rd child node + ...
        self.hash_code += len(self.children) * node.hash_code

        # childhash code is child1 XOR child2 XOR ...
        self.childhash_code ^= node.hash_code

        # if it is a leaf node, add itself to the leaf sets
        # of all its ancesters
        if node.widget_id != "Row" and node.widget_id != "Column":
            for ancestor, _ in node.path_to_root:
                ancestor.leaves.append(node.widget_id)

# the added node in S2
class addNode():
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return "Add node '" + str(self.node.widget_id) + "' in S2"

# the removed node in S1
class removeNode():
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return "Remove node '" + str(self.node.widget_id) + "' from S1" 

# the moved node in S1 to node in S2
class moveNode():
    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node

    def __str__(self):
        return "Move node '" + str(self.from_node.widget_id) \
              + "' in S1 to node '" + str(self.to_node.widget_id) \
              + "' in S2"

# the replace node in S1 with node in S2
class replaceNode():
    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node

    def __str__(self):
        return "Replace node '" + str(self.from_node.widget_id) \
              + "' in S1 with node '" + str(self.to_node.widget_id) \
              + "' in S2"

# change the type of the node
class changeType():
    def __init__(self, node, from_type, to_type):
        self.node = node
        self.from_type = from_type
        self.to_type = to_type

    def __str__(self):
        return "The type of node '" + str(self.node.widget_id) \
              + "' is changed from '" + str(self.from_type) \
              + "' to '" + str(self.to_type) + "'"

# change the children order of the node
class changeChildrenOrder():
    def __init__(self, node, from_order, to_order):
        self.node = node
        self.from_order = from_order
        self.to_order = to_order

    def __str__(self):
        from_str = ""
        for w in self.from_order:
            from_str += str(w.widget_id) + ","
        from_str = from_str[:-1]
        to_str = ""
        for w in self.to_order:
            to_str += str(w.widget_id) + ","
        to_str = to_str[:-1]
        return "The children order of node '" + str(self.node.widget_id) \
              + "' is changed from '" + from_str \
              + "' to '" + to_str + "'"

# construct tree for the layout
def construct_tree(subtree, hash_to_node, childhash_to_node, \
                                        parent=None, child_num=1):

    # create a internal node
    if type(subtree) == dict and subtree != {}:
        node_type = list(subtree.keys())[0]
        node = Node(parent, node_type, child_num)
        child_num = 1
        for child_subtree in subtree[node_type]:
            child = construct_tree(child_subtree, hash_to_node, \
                                childhash_to_node, node, child_num)
            node.add_child(child)
            child_num += 1

    # create a leaf node
    else:
        node = Node(parent, subtree, child_num)

    # add hash maps
    hash_to_node[node.hash_code] = node
    childhash_to_node[node.childhash_code] = node

    return node


# check the difference between corrsponding 
# siblings in S1 and S2
def check_diff(S1, S2, S1_hash_to_node, \
                S1_childhash_to_node, S2_hash_to_node, \
                S2_childhash_to_node, changes, moved_widgets):

    # hashtable from element in S1 to element in S2 
    # empty to start with
    pairs = {}

    # copy S1 and S2 to keep track of remaining nodes
    S1_curr = S1[:]
    S2_curr = S2[:]

    # if there is only element, 
    # then it must be paired and processed
    if len(S2_curr) == 1:
        only_element = True
    else: 
        only_element = False

    # loop over nodes in S2
    for s2 in S2:

        # if s2 is originally in the whole tree T1
        if s2.hash_code in S1_hash_to_node.keys():

            # get the correponding node in T1
            s1 = S1_hash_to_node[s2.hash_code]

            # remove them from S1 and S2
            if s1 in S1_curr:
                S1_curr.remove(s1)
            S2_curr.remove(s2)

            # if s1 not in S1, then it is moved from 
            # somewhere
            if s1 not in S1:
                if s1 not in moved_widgets:
                    changes.append(moveNode(s1, s2))
                    moved_widgets.append(s1)
            else:
                pairs[s2] = s1

    # loop over nodes in S2_curr
    for s2 in S2_curr:

        # if element s1 in T1 with same childHashCode as s2
        if s2.childhash_code in S1_childhash_to_node.keys():

            # get the correponding node in T1
            s1 = S1_childhash_to_node[s2.childhash_code]

            # remove them from S1 and S2
            if s1 in S1_curr:
                S1_curr.remove(s1)
            S2_curr.remove(s2)

            # if s1 not in S1, then it is moved
            # from somewhere
            if s1 not in S1:
                if s1 not in moved_widgets:
                    changes.append(moveNode(s1, s2))
                    moved_widgets.append(s1)
            else:
                pairs[s2] = s1

            # check whether node type is changed
            if s1.widget_id != s2.widget_id:
                changes.append(changeType(s1, \
                    s1.widget_id, s2.widget_id))

            # check whether children order is changed
            if s1.children_codes != s2.children_codes:
                changes.append(changeChildrenOrder(s1, \
                        s1.children, s2.children))

    # pair those with the most similar nodes
    while S2_curr != []:

        # find the pair of nodes with the 
        # largest similaries
        max_sim = 0
        best_pair = None
        for s2 in S2_curr:
            for s1 in S1_curr:

                # get the number of common leaves
                similarity = 0
                for leaf in s2.leaves:
                    if leaf in s1.leaves:
                        similarity += 1

                # get the one with the most similar leaves
                if similarity > max_sim or only_element:
                    max_sim = similarity
                    best_pair = (s1, s2)

        # found the best pair
        if max_sim != 0 or only_element:
            s1_best, s2_best = best_pair

            if max_sim > 0:
                pairs[s2_best] = s1_best

            # remove them from S1 and S2
            S1_curr.remove(s1_best)
            S2_curr.remove(s2_best)

            # change type 
            if s1_best.widget_id != s2_best.widget_id:
                changes.append(changeType(s1_best, \
                    s1_best.widget_id, s2_best.widget_id))

            # recursively call the next level
            if s1_best.widget_id != "Row" and s1_best.widget_id != "Column":
                check_diff([s1_best], s2_best.children, S1_hash_to_node, \
                        S1_childhash_to_node, S2_hash_to_node, \
                        S2_childhash_to_node, changes, moved_widgets)
            elif s2_best.widget_id != "Row" and s2_best.widget_id != "Column":
                check_diff(s1_best.children, [s2_best], S1_hash_to_node, \
                        S1_childhash_to_node, S2_hash_to_node, \
                        S2_childhash_to_node, changes, moved_widgets)
            else:
                check_diff(s1_best.children, s2_best.children, S1_hash_to_node, \
                        S1_childhash_to_node, S2_hash_to_node, \
                        S2_childhash_to_node, changes, moved_widgets)
        else:
            break

    # check for order changes in paired elements
    S1_paired = [s1 for s1 in S1 if s1 in pairs.values()]
    S2_paired = [s2 for s2 in S2 if s2 in pairs.keys()]

    # replace s2 in S2_paired by pairs[s2]
    for i in range(len(S2_paired)):
        S2_paired[i] = pairs[S2_paired[i]]

    # check the order
    if S1_paired != S2_paired:
        changes.append(changeChildrenOrder(S1_paired[0].parent, \
                                    S1_paired, S2_paired))

    # get the indices of the paired widgets
    S1_paired_index = [S1.index(s1) for s1 in S1_paired]
    S2_paired_index = [S1.index(s2) for s2 in S2_paired]

    # get how many paired ones are before this one
    add_index_list = []
    for s2 in S2_curr:
        add_index_list.append(sum([i < S2.index(s2) for i in S2_paired_index]))

    # if S1 still has nodes, then it is removed
    for s1 in S1_curr:
        if s1.childhash_code not in S2_childhash_to_node.keys():
            remove_index = sum([i < S1.index(s1) for i in S1_paired_index])
            if remove_index in add_index_list:
                s2 = S2_curr[add_index_list.index(remove_index)]
                changes.append(replaceNode(s1, s2))
                S2_curr.remove(s2)
            else:
                changes.append(removeNode(s1))
        else:
            # check move operations have been added if they
            # are moved to some where
            if s1 not in moved_widgets:
                changes.append(moveNode(s1, S2_childhash_to_node[s1.childhash_code]))
                moved_widgets.append(s1)

    # if S2 still has nodes, then it is added
    for s2 in S2_curr:
        changes.append(addNode(s2))


def detect_tree_diff(tree_json1, tree_json2):

    # a hashtable mapping hash codes 
    # to corresponding node objects 
    S1_hash_to_node = {}
    S2_hash_to_node = {}

    # a hashtable mapping childhash codes 
    # to corresponding node objects 
    S1_childhash_to_node = {}
    S2_childhash_to_node = {}

    # construct the trees
    tree1 = construct_tree(tree_json1, S1_hash_to_node, \
                                    S1_childhash_to_node)
    tree2 = construct_tree(tree_json2, S2_hash_to_node, \
                                    S2_childhash_to_node)

    # get difference set
    changes = []
    moved_widgets = []
    check_diff([tree1], [tree2], S1_hash_to_node, \
                    S1_childhash_to_node, S2_hash_to_node, \
                    S2_childhash_to_node, changes, moved_widgets)
    
    # print different result
    for op in changes:
        print(op, "==")

    return changes
  
