import bpy, os, shutil

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def clean_soft():
    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    # Prepare to handle long path issue by using UNC path prefix
    def get_long_path(path):
        return f"\\\\?\\{os.path.abspath(path)}"

    # Create a "nx-build" folder path
    project_folder = os.path.join(currentSaveDir, "nx-build")

    # Output folder path
    out_folder = os.path.join(currentSaveDir, "out")

    # Use the long path version for deleting
    if os.path.exists(project_folder):
        shutil.rmtree(get_long_path(project_folder), ignore_errors=False)

    if os.path.exists(out_folder):
        shutil.rmtree(get_long_path(out_folder), ignore_errors=False)

    # Optionally, reset the directory to avoid changing the working directory of the script
    os.chdir(currentSaveDir)


def clean_hard():

    currentSavePath = bpy.data.filepath
    currentSaveDir = os.path.dirname(currentSavePath)

    os.chdir(currentSaveDir)

    #Create a "nx-build" folder
    project_folder = "nx-build"

    #Output folder
    out_folder = "out"

    if(os.path.exists(project_folder)):
        os.system('rm -fr "%s"' % project_folder)

    if(os.path.exists(out_folder)):
        os.system('rm -fr "%s"' % out_folder)