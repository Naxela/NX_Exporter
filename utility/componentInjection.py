import bpy

def fetchInjectionHeader():

    if bpy.context.scene.NX_SceneProperties.nx_injection_header is not None:

        return [bpy.context.scene.NX_SceneProperties.nx_injection_header.as_string()]
    
def createInjectionFile(filepath, injectionHeader, injectionData):

    f = open(filepath, "w")

    if injectionHeader is not None:
        f.write(injectionHeader[0])

    f.write("\n")

    f.write(
"""export default function ComponentInjection(){
    
    return (
        <>
""")
    

    for item in injectionData:
        f.write(item)
    

    f.write(
"""        </>
    )
}
""")


    f.close()

def insertInjectionData(filepath, data, line):
    if data is not None:
        # Read the original content of the file
        with open(filepath, 'r') as file:
            lines = file.readlines()

        # Convert the array to a list of strings with newline characters
        array_strings = [item + '\n' for item in data]

        if line == 0:
            # Special handling for inserting at the beginning of the file
            modified_lines = array_strings + lines
        else:
            # The line number where you want to insert the array
            insert_at_line = line

            # Adjust the insert position for zero-based indexing
            insert_at_index = insert_at_line - 1

            # Insert the array into the list of lines
            modified_lines = lines[:insert_at_index] + array_strings + lines[insert_at_index:]

        # Write the modified content back to the file
        with open(filepath, 'w') as file:
            file.writelines(modified_lines)