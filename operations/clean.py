import bpy, os, shutil

def clean_soft():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    os.chdir(currentSaveDir)

    #Create a "nx-build" folder
    project_folder = "nx-build"

    #Output folder
    out_folder = "out"

    if(os.path.exists(project_folder)):
        shutil.rmtree(project_folder, ignore_errors=True)

    if(os.path.exists(out_folder)):
        shutil.rmtree(out_folder, ignore_errors=True)