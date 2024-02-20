import bpy, os, shutil, socket
from typing import Any, Type

# We presume that the TCP is running on the same machine
host = '127.0.0.1'
port = 12345  # Ensure this matches the port your TCP server is listening on

# Any object can act as a message bus owner
msgbus_owner = object()

patch_id = 0
"""Current patch id"""

__running = False
"""Whether live patch is currently active"""

def start():
    """Start the live patch session."""
    print("Live patch session started")

    listen(bpy.types.Object, "location", "obj_location")
    listen(bpy.types.Object, "rotation_euler", "obj_rotation")
    listen(bpy.types.Object, "scale", "obj_scale")

    global __running
    __running = True

def stop():
    """Stop the live patch session."""
    global __running, patch_id
    if __running:
        __running = False
        patch_id = 0

        print("Live patch session stopped")
        bpy.msgbus.clear_by_owner(msgbus_owner)

def listen(rna_type: Type[bpy.types.bpy_struct], prop: str, event_id: str):
    """Subscribe to '<rna_type>.<prop>'. The event_id can be choosen
    freely but must match with the id used in send_event().
    """
    print("LISTENING!")
    bpy.msgbus.subscribe_rna(
        key=(rna_type, prop),
        owner=msgbus_owner,
        args=(event_id, ),
        notify=send_event
        #options={"PERSISTENT"}
    )

def send_event(event_id: str, opt_data: Any = None):
    """Send the result of the given event to Krom."""
    if not __running:
        return

    if hasattr(bpy.context, 'object') and bpy.context.object is not None:
        obj = bpy.context.object.name

        if bpy.context.object.mode == "OBJECT":
            if event_id == "obj_location":
                vec = bpy.context.object.location
                js = f'Linker.moveObject("{obj}", [{vec[0]}, {vec[1]}, {vec[2]}]);'
                
                print("PATCH: " + js)
                #write_patch(js)

# import socket

# def send_tcp_message():
#     host = '127.0.0.1'
#     port = 12345  # Ensure this matches the port your TCP server is listening on

#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((host, port))
#         s.sendall(b'Hello from Blender!')
#         # Optionally wait for a response, though this example TCP server doesn't send one back
#         # data = s.recv(1024)

#     # print('Received', repr(data))

# send_tcp_message()