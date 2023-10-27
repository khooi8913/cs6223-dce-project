import os
import subprocess
import argparse

from pprint import pprint
from insert_markers import instrument_markers

P4C_PATH = os.environ['P4C_PATH'] 
P4C_BUILD_PATH = os.path.join(P4C_PATH, "build")
P4TEST_PATH = os.path.join(P4C_BUILD_PATH, "p4test")
P4C_BM2_PATH = os.path.join(P4C_BUILD_PATH, "p4c-bm2-ss")
BLUDGEON_PATH = os.path.join(P4C_BUILD_PATH, "p4bludgeon")

assert os.path.exists(P4TEST_PATH) and os.path.exists(BLUDGEON_PATH) and os.path.exists(P4C_BM2_PATH)

def get_desired_constructs(p4_code: str):
    desired_constructs = ["if", "else"]
    undesired_constructs = ["switch"]
    return any(cst in p4_code for cst in desired_constructs) and not any(cst in p4_code for cst in undesired_constructs)

def compilation_check(arch, output_path):
    if arch == 'top':
        command = " ".join([P4TEST_PATH, output_path])
    if arch == 'v1model':
        command = " ".join([P4C_BM2_PATH, output_path])
    ret_val, output = subprocess.getstatusoutput(command)
    if ret_val != 0:
        print(output)
    return True if ret_val == 0 else False

def execute_bludgeon_command(arch, output_path):
    command = " ".join([BLUDGEON_PATH, "--output", output_path, "--arch", arch])
    ret_val, output = subprocess.getstatusoutput(command)
    return output if ret_val == 0 else ""


def generate_p4_program(arch, output_path):
    """Returns a generated P4 program given a specific architecture."""
    output = execute_bludgeon_command(arch, output_path)
    # [--Wwarn=mismatch] warning: 3w8: value does not fit in 3 bits
    # Could not find writable bit lval for assignment!
    while 'mismatch' in str(output) or 'lval' in str(output):
        output = execute_bludgeon_command(arch, output_path)
    
    p4_code = ""
    with open(output_path) as f:
        p4_code = f.read()
    return p4_code

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--arch', type=str, default='top',
        choices=['top', 'tna', 'v1model'],
        help='target architecture for the generated p4 program'
    )

    parser.add_argument(
        '--output-path', default='./generated/',
        help='output path for the generated p4 programs'
    )

    parser.add_argument(
        '--instrumented-path', default='./instrumented/',
        help='output path for the instrumented p4 programs'
    )

    parser.add_argument(
        '--num-programs', type=int, default=100,
        help='number of p4 programs to generate'
    )

    args = parser.parse_args()
    pprint(args)
    
    output_path = args.output_path
    instrumented_path = args.instrumented_path
    arch = args.arch
    num_programs = args.num_programs 

    output_path = os.path.join(output_path, arch)
    instrumented_path = os.path.join(instrumented_path, arch)
    
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    if not os.path.exists(instrumented_path):
        os.makedirs(instrumented_path, exist_ok=True)

    assert os.path.exists(output_path)

    for i in range(num_programs):
        print("====================")
        print("Generating program #" + str(i))
        curr_output_path = os.path.join(output_path, "program_{:03d}.p4".format(i))
        p4_code = generate_p4_program(arch=arch, output_path=curr_output_path)
        has_desired_construct = get_desired_constructs(p4_code)
        is_can_compile = compilation_check(arch, curr_output_path)
        while True:
            if has_desired_construct and is_can_compile:
                break
            p4_code = generate_p4_program(arch=arch, output_path=curr_output_path)
            has_desired_construct = get_desired_constructs(p4_code)
            is_can_compile = compilation_check(arch, curr_output_path)
        print("Program generated", curr_output_path)
        
        print("Instrumenting markers...")
        curr_instr_path = os.path.join(instrumented_path, "program_{:03d}.p4".format(i))
        p4_code_with_markers = instrument_markers(p4_code)
        with open(curr_instr_path, 'w') as f:
            f.write(p4_code_with_markers)
        print("Writing to", curr_instr_path)
        print("====================\n")
        
if __name__ == '__main__':
    main()