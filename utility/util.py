import bpy, math, mathutils, os, json

#MATH/VECTOR/MATRIX HELPERS
def get_object_matrix_y_axis(obj):
    matrix_world = obj.matrix_world

    # Create a rotation matrix (rotating -90 degrees around X-axis)
    rot_x_90 = mathutils.Matrix.Rotation(-math.pi / 2, 4, 'X')

    # Apply the rotation to the world matrix
    adjusted_matrix = rot_x_90 @ matrix_world

    # Flatten the matrix into a list
    matrix_flat = [val for row in adjusted_matrix for val in row]
    return(matrix_flat)

def ensureFilesave():

    currentSavePath = bpy.data.filepath

    if currentSavePath:
        return True
    else:
        return False

def getObjectParent(obj):
    if(obj.parent):
        return obj.parent.name
    else:
        return None

def is_generated_project_present():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    project_name = "nx-project"
    directory = os.path.join(currentSaveDir, project_name)  # Set your desired path here

    package_json_path = os.path.join(directory, 'package.json')

    # Check if package.json exists
    if not os.path.isfile(package_json_path):
        return False

    # Optional: Validate the contents of package.json
    try:
        with open(package_json_path, 'r') as file:
            package_data = json.load(file)

        return True
        # You can add more checks here to validate the structure of package.json
        # For example, check if certain fields exist:
        # if 'name' in package_data and 'scripts' in package_data:
        #     if package_data['name'] == 'test':
        #         return True
        #     else:
        #         return False
        # else:
        #     return False

    except json.JSONDecodeError:
        # The file is not a valid JSON
        return False

    return False

def get_project_path():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    project_name = "nx-project"
    directory = os.path.join(currentSaveDir, project_name)  # Set your desired path here

    return directory

def get_assets_path():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    project_name = "nx-project"
    directory = os.path.join(currentSaveDir, project_name, "assets")  # Set your desired path here

    return directory

def get_sources_path():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    project_name = "nx-project"
    directory = os.path.join(currentSaveDir, project_name, "sources")  # Set your desired path here

    return directory

def get_shaders_path():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    project_name = "nx-project"
    directory = os.path.join(currentSaveDir, project_name, "shaders")  # Set your desired path here

    return directory