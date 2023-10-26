import os
import subprocess
import argparse
import tiktoken

from pprint import pprint

P4C_PATH = os.environ['P4C_PATH'] 
P4C_BUILD_PATH = os.path.join(P4C_PATH, "build")
BLUDGEON_PATH = os.path.join(P4C_BUILD_PATH, "p4bludgeon")

assert os.path.exists(BLUDGEON_PATH)

def get_num_tokens(p4_code: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(p4_code))
    return num_tokens

def get_desired_constructs(p4_code: str):
    desired_constructs = ["if", "else", "switch"]
    return any(cst in p4_code for cst in desired_constructs)

def execute_command(arch, output_path):
    command = " ".join([BLUDGEON_PATH, "--output", output_path, "--arch", arch])
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        output = "mismatch"
    return output

def generate_p4_program(arch, output_path):
    """Returns a generated P4 program given a specific architecture."""
    output = execute_command(arch, output_path)
    # [--Wwarn=mismatch] warning: 3w8: value does not fit in 3 bits
    # Could not find writable bit lval for assignment!
    while 'mismatch' in str(output) or 'lval' in str(output):
        output = execute_command(arch, output_path)
    
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
        '--output-path', required=True, default='./output/',
        help='output path for the generated p4 programs'
    )

    parser.add_argument(
        '--max-tokens', type=int, default=1800,
        help='maximum number of tokens in a p4 program'
    )

    parser.add_argument(
        '--num-programs', type=int, default=100,
        help='number of p4 programs to generate'
    )

    args = parser.parse_args()
    pprint(args)
    
    output_path = args.output_path
    arch = args.arch
    max_tokens = args.max_tokens
    num_programs = args.num_programs 

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    assert os.path.exists(output_path)

    for i in range(num_programs):
        curr_output_path = os.path.join(output_path, "program_{:03d}".format(i))
        p4_code = generate_p4_program(arch=arch, output_path=curr_output_path)
        num_tokens = get_num_tokens(p4_code=p4_code)
        has_desired_construct = get_desired_constructs(p4_code)
        while num_tokens >= max_tokens and not has_desired_construct:
            p4_code = generate_p4_program(arch=arch, output_path=curr_output_path)
            num_tokens = get_num_tokens(p4_code=p4_code)
            has_desired_construct = get_desired_constructs(p4_code)
        
if __name__ == '__main__':
    main()