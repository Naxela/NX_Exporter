import bpy, os

from .. utility import util

def create_javascript_file(classname, fileformat):

    sources_path = util.get_sources_path()

    if(fileformat == 'TypeScript'):
        filename = os.path.join(sources_path, classname) + ".tsx"
    else:
        filename = os.path.join(sources_path, classname) + ".jsx"

    template = '''
export default class {class_name} {{
    constructor(object) {{
        this.object = object;
    }}

    NotifyOnInit() {{
        // Initial setup logic here
    }}

    NotifyOnUpdate() {{
        // Update logic here
    }}

}}
'''

    formatted_template = template.format(class_name=classname)

    with open(filename, 'w') as f:
        f.write(formatted_template)

    return True