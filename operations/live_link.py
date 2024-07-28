import bpy, os, shutil, socket
from typing import Any, Type

from ..utility import util

# We presume that the TCP is running on the same machine
host = '127.0.0.1'
port = 12345  # Ensure this matches the port your TCP server is listening on
connection = None

# Any object can act as a message bus owner
msgbus_owner = object()

patch_id = 0
"""Current patch id"""

__running = False
"""Whether live patch is currently active"""

def connect_to_server():
    print("Connect...")
    """Attempt to connect to the server."""
    global connection
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        connection.connect((host, port))
        connection.sendall(b'Init from Blender!')
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")

def start():
    """Start the live patch session."""
    print("Live patch session started")
    global __running
    # Initialize and connect the socket
    connect_to_server()

    listen(bpy.types.Object, "location", "obj_location")
    listen(bpy.types.Object, "rotation_euler", "obj_rotation")
    listen(bpy.types.Object, "scale", "obj_scale")

    for light_type in (bpy.types.AreaLight, bpy.types.PointLight, bpy.types.SpotLight, bpy.types.SunLight):
        listen(light_type, "color", "light_color")
        listen(light_type, "energy", "light_energy")

    if depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_handler)
    
    __running = True

def stop():
    """Stop the live patch session."""
    global __running, connection
    if __running:
        __running = False
        if connection:
            try:
                connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
            finally:
                connection = None
        print("Live patch session stopped")
        bpy.msgbus.clear_by_owner(msgbus_owner)

    if depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_handler)

def listen(rna_type: Type[bpy.types.bpy_struct], prop: str, event_id: str):
    """Subscribe to '<rna_type>.<prop>'. The event_id can be choosen
    freely but must match with the id used in send_event().
    """
    #print("LISTENING!")
    bpy.msgbus.subscribe_rna(
        key=(rna_type, prop),
        owner=msgbus_owner,
        args=(event_id, ),
        notify=send_event
        #options={"PERSISTENT"}
    )

def depsgraph_update_handler(scene, depsgraph):
    # This iterates over all the updates in the depsgraph
    for update in depsgraph.updates:
        # Check if the update is for an object
        if isinstance(update.id, bpy.types.Object):

            loc = update.id.location
            rot = update.id.rotation_euler
            scale = update.id.scale

            objID = update.id["nx_id"]

            #cmd = f'MAX.moveObject("{objID}", [{loc[0]}, {loc[2]}, {-loc[1]}]); app.rotateObject("{objID}", [{rot[0]}, {rot[2]}, {-rot[1]}]); app.scaleObject("{objID}", [{scale[0]}, {scale[2]}, {scale[1]}]);'

            #We don't know whether it was moved, rotated or scaled, so we copy the matrix
            matrix = util.get_object_matrix_y_axis(update.id)
            cmd = f'NAX.applyMatrix("{objID}", {matrix});'

            #cmd = 

            try:
                connection.sendall(cmd.encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError) as e:
                print(f"Connection error: {e}, attempting to reconnect...")
                connect_to_server()  # Attempt to reconnect
            except Exception as e:
                print(f"Unexpected error: {e}")
            #matrix = f'app.applyMatrix("{objID}", [{vec[0]}, {vec[2]}, {-vec[1]}]);'

            #print(cmd)

def send_event(event_id: str, opt_data: Any = None):
    """Send the result of the given event to Krom."""
    global connection, __running
    if not __running or connection is None:
        return
    
    if hasattr(bpy.context, 'object') and bpy.context.object is not None:
        obj = bpy.context.object.name
        objID = bpy.context.object["nx_id"]
        if bpy.context.object.mode == "OBJECT":
            if event_id == "obj_location":
                #vec = bpy.context.object.location
                #cmd = f'app.moveObject("{objID}", [{vec[0]}, {vec[2]}, {-vec[1]}]);'

                matrix = util.get_object_matrix_y_axis(update.id)
                cmd = f'NAX.applyMatrix("{objID}", {matrix});'

                try:
                    connection.sendall(cmd.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Connection error: {e}, attempting to reconnect...")
                    connect_to_server()  # Attempt to reconnect
                except Exception as e:
                    print(f"Unexpected error: {e}")

            if event_id == "obj_rotation":
                #vec = bpy.context.object.rotation_euler
                #cmd = f'app.rotateObject("{objID}", [{vec[0]}, {vec[2]}, {-vec[1]}]);'

                matrix = util.get_object_matrix_y_axis(update.id)
                cmd = f'NAX.applyMatrix("{objID}", {matrix});'

                try:
                    connection.sendall(cmd.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Connection error: {e}, attempting to reconnect...")
                    connect_to_server()  # Attempt to reconnect
                except Exception as e:
                    print(f"Unexpected error: {e}")

            if event_id == "obj_scale":
                #vec = bpy.context.object.scale
                #cmd = f'app.scaleObject("{objID}", [{vec[0]}, {vec[2]}, {vec[1]}]);'

                matrix = util.get_object_matrix_y_axis(update.id)
                cmd = f'NAX.applyMatrix("{objID}", {matrix});'

                try:
                    connection.sendall(cmd.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Connection error: {e}, attempting to reconnect...")
                    connect_to_server()  # Attempt to reconnect
                except Exception as e:
                    print(f"Unexpected error: {e}")

            elif event_id == 'light_color':

                light: bpy.types.Light = bpy.context.object.data
                vec = light.color
                
                cmd = f'NAX.setLightColor("{objID}", [{vec[0]}, {vec[1]}, {vec[2]}]);'
                
                try:
                    connection.sendall(cmd.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Connection error: {e}, attempting to reconnect...")
                    connect_to_server()  # Attempt to reconnect
                except Exception as e:
                    print(f"Unexpected error: {e}")

            elif event_id == 'light_energy':

                light: bpy.types.Light = bpy.context.object.data
                vec = light.energy
                
                cmd = f'NAX.setLightStrength("{objID}", {vec});'

                try:
                    connection.sendall(cmd.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Connection error: {e}, attempting to reconnect...")
                    connect_to_server()  # Attempt to reconnect
                except Exception as e:
                    print(f"Unexpected error: {e}")