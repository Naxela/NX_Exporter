import bpy
from nodeitems_utils import NodeCategory, NodeItem

# Define a new node tree type
class MyCustomNodeTree(bpy.types.NodeTree):
    '''A custom node tree type that will hold our custom nodes'''
    bl_idname = 'CustomNodeTree'
    bl_label = 'Custom Node Tree'
    bl_icon = 'NODETREE'

# Base class for all custom nodes in this tree
class MyCustomTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CustomNodeTree'

# Example custom node
class MyCustomNode(bpy.types.Node, MyCustomTreeNode):
    '''A custom node'''
    bl_idname = 'MyCustomNode'
    bl_label = 'Custom Node'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Output")

    def update(self):
        # Update node logic goes here
        pass

# Example custom socket
class MyCustomSocket(bpy.types.NodeSocket):
    '''A custom socket of type 'Float' '''
    bl_idname = 'MyCustomSocketFloat'
    bl_label = 'Custom Float Socket'

    # Default value
    value: bpy.props.FloatProperty(name="Value")

    def draw(self, context, layout, node, text):
        layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)  # Orange

class MyCustomNodePanel(bpy.types.Panel):
    '''Creates a Panel in the node editor'''
    bl_label = "Custom Nodes"
    bl_idname = "NODE_PT_custom"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Custom Tab'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CustomNodeTree'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Put your UI elements here")

# Define the custom node category
class MyCustomNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CustomNodeTree'

    items = [
        NodeItem("MyCustomNode"),
    ]

# Register and unregister functions that will add the node category
def register_node_categories():
    node_categories = [
        MyCustomNodeCategory("MY_CUSTOM_NODES", "Custom Nodes", items=[
            NodeItem("MyCustomNode"),
        ]),
    ]

    from nodeitems_utils import register_node_categories
    register_node_categories("CUSTOM_NODES", node_categories)

def unregister_node_categories():
    from nodeitems_utils import unregister_node_categories
    unregister_node_categories("CUSTOM_NODES")

# Register and unregister functions
def register():
    print("Registering Nodes")
    bpy.utils.register_class(MyCustomNodeTree)
    bpy.utils.register_class(MyCustomNode)
    bpy.utils.register_class(MyCustomSocket)
    bpy.utils.register_class(MyCustomNodePanel)

    register_node_categories()  # Register the node category

def unregister():
    unregister_node_categories()  # Unregister the node category

    bpy.utils.unregister_class(MyCustomNodeTree)
    bpy.utils.unregister_class(MyCustomNode)
    bpy.utils.unregister_class(MyCustomSocket)
    bpy.utils.unregister_class(MyCustomNodePanel)

if __name__ == "__main__":
    register()