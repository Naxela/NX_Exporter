import bpy, os

from .. utility import util

def create_javascript_file(classname):

    sources_path = util.get_sources_path()

    filename = os.path.join(sources_path, classname) + ".js"

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