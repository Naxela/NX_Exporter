class NodeScriptCompiler:
    def __init__(self, node_tree):
        self.node_tree = node_tree
        self.script_lines = []

    def compile(self):
        # Start with the OnInit node and compile the script from there
        init_node = self.find_node_of_type('OnInit')
        if init_node:
            self.compile_node(init_node)
        return '\n'.join(self.script_lines)

    def find_node_of_type(self, node_type):
        for node in self.node_tree.nodes:
            if node.bl_idname == node_type:
                return node
        return None

    def compile_node(self, node):
        # Depending on the type of node, generate the corresponding JS code
        if node.bl_idname == 'OnInit':
            self.script_lines.append('document.addEventListener("DOMContentLoaded", function() {')
            self.compile_connected_nodes(node)
            self.script_lines.append('});')

        elif node.bl_idname == 'Print':
            input_socket = node.inputs.get('Message')
            if input_socket and input_socket.is_linked:
                connected_node = input_socket.links[0].from_node
                message = self.compile_node(connected_node)  # Recursively compile the connected node
                self.script_lines.append(f'console.log({message});')

        elif node.bl_idname == 'Message':
            # Assuming the message node has a property to hold the text
            return f'"{node.message_property}"'

    def compile_connected_nodes(self, node):
        for output in node.outputs:
            if output.is_linked:
                for link in output.links:
                    self.compile_node(link.to_node)
