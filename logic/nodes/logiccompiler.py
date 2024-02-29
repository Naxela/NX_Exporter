class LogicNode:
    def __init__(self):
        self.inputs = []
        self.output = None

    def get_input_value(self, index):
        # In an actual implementation, this method would be more complex,
        # handling cases where inputs are not connected or are of incorrect type.
        return self.inputs[index].get_value()

    def run(self):
        pass

    def get_value(self):
        return self.output

class PrintNode(LogicNode):
    def __init__(self):
        super().__init__()

    def run(self):
        value = self.get_input_value(1)
        self.output = f'console.log("{value}");'

class MessageNode(LogicNode):
    def __init__(self, message):
        super().__init__()
        self.output = message

class NodeTree:
    def __init__(self, name):
        self.name = name
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def compile_to_js(self):
        js_script = ""
        for node in self.nodes:
            node.run()
            if node.output:
                js_script += node.output + "\n"
        return js_script

# Example usage
node_tree = NodeTree("ExampleTree")

# Create a message node with a message to print
message_node = MessageNode("Hello, World!")
node_tree.add_node(message_node)

# Create a print node and connect it to the message node's output
print_node = PrintNode()
print_node.inputs.append(message_node)
node_tree.add_node(print_node)

# Compile the node tree to JavaScript
js_script = node_tree.compile_to_js()
print(js_script)
