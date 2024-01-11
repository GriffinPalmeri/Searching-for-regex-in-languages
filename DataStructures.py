class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class Stack:
    def __init__(self) -> None:
        self.head = Node("head")
        self.size = 0

    def peek(self):
        if self.isEmpty():
            raise Exception("Error: Attempted to peek on an empty stack")
        return self.head.next.value

    def pop(self):
        if self.isEmpty():
            raise Exception("Error: Attempted to pop from an empty stack")
        removed_node = self.head.next
        self.head.next = self.head.next.next
        self.size -= 1
        return removed_node.value

    def push(self, value):
        new_node = Node(value)
        new_node.next = self.head.next
        self.head.next = new_node
        self.size += 1

    def __str__(self):
        current_node = self.head.next
        output = ""
        while current_node:
            output += str(current_node.value) + "->"
            current_node = current_node.next
        return output[:-2]

    def getSize(self):
        return self.size

    def isEmpty(self):
        return self.size == 0


class SyntaxTreeNode:
    def __init__(self, node_type, value=None):
        self.node_type = node_type
        self.value = value
        self.left_child = None
        self.right_child = None
        self.nfa_for_node = None

    def add_child(self, child_node):
        if(self.right_child is None):
            self.right_child = child_node
        elif(self.left_child is None):
            self.left_child = child_node
        else:
            raise Exception("There are already two children of this node")
