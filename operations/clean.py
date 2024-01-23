import bpy, os, shutil

def clean_soft():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    os.chdir(currentSaveDir)

    #Create a "nx-build" folder
    project_folder = "nx-build"

    if(os.path.exists(project_folder)):
        shutil.rmtree(project_folder)