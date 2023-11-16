import re
import os
import sys

def insert_pre_marker(p4_code):
    # Function to insert a marker after the open brace
    def insert_marker(match):
        return match.group(1) + " { \n            // MARKER"
    # Regular expressions to match action blocks and if-else statements in P4
    action_pattern = r'(action\s+\w+\s*\([^)]*\))\s*{'
    # if_else_pattern = r'(if\s*\([^)]*\)|else)\s*{'
    if_else_pattern = r'(if\s*\(.*?\)|else)\s*{'
    # Insert markers for action blocks
    p4_code_with_markers = re.sub(action_pattern, insert_marker, p4_code)
    # Insert markers for if-else statements
    p4_code_with_markers = re.sub(if_else_pattern, insert_marker, p4_code_with_markers)
    return p4_code_with_markers

def replace_pre_marker(p4_code_with_marker):
    # regex = re.compile('// MARKER')
    counter = 0
    while "// MARKER" in p4_code_with_marker:
        text_to_replace = 'marker_dce{:02d}();'.format(counter)
        counter = counter + 1
        p4_code_with_marker = p4_code_with_marker.replace("// MARKER", text_to_replace, 1)
    return counter, p4_code_with_marker

def declare_marker_as_extern(num_markers, p4_code_with_marker):
    extern_str = ["@noSideEffects\nextern void marker_dce{:02d}();".format(i) for i in range(num_markers)]
    extern_str = "\n".join(extern_str)
    include_str = "#include <core.p4>"
    index_to_insert = p4_code_with_marker.rindex("#include <core.p4>")
    index_to_insert = index_to_insert + len(include_str)
    p4_code_with_marker = p4_code_with_marker[:index_to_insert] + "\n" + extern_str + "\n" + p4_code_with_marker[index_to_insert+1:]
    # print(p4_code_with_marker)
    return p4_code_with_marker

def instrument_markers(p4_code):
    p4_code_with_marker = insert_pre_marker(p4_code)
    num_markers, p4_code_with_marker = replace_pre_marker(p4_code_with_marker)
    p4_code_with_marker = declare_marker_as_extern(num_markers, p4_code_with_marker)
    return p4_code_with_marker

if __name__ == "__main__":
    generated_dir = "generated/top/"
    instrumented_dir = "instrumented/top"
    
    os.makedirs(instrumented_dir, exist_ok=True)
    assert os.path.exists(generated_dir) and os.path.exists(instrumented_dir)
    
    p4_code_files = os.listdir(generated_dir)
    for p4 in p4_code_files:
        current_p4_code_path = os.path.join(generated_dir, p4) 
        output_p4_code_path = os.path.join(instrumented_dir, p4)
        p4_code = ""
        with open(current_p4_code_path) as f:
            p4_code = f.read()
        p4_code = instrument_markers(p4_code)
        with open(output_p4_code_path, 'w') as f:
            f.write(p4_code)