import os
import argparse
import shutil

from pprint import pprint

# p4lang/p4c container versions
docker_p4c_versions = ["stable", "1.2.4.3", "1.2.4.4", "1.2.4.5", "1.2.3.0", "1.2.3.9"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--arch', type=str, default='top',
        choices=['top', 'tna', 'v1model'],
        help='target architecture for the generated p4 program'
    )

    parser.add_argument(
        '--instrumented-path', default='./instrumented/',
        help='path for the instrumented programs'
    )

    parser.add_argument(
        '--target-path', default='./output/',
        help='target path for the IRs'
    )

    parser.add_argument(
        '--compiler-bug-path', default='./compiler_bug/',
        help='path to store the problematic programs'
    )

    parser.add_argument(
        '--num-programs', type=int, default=100,
        help='number of p4 programs to generate'
    )

    args = parser.parse_args()
    pprint(args)
       
    arch = args.arch
    instrumented_path = args.instrumented_path
    instrumented_path = os.path.join(instrumented_path, arch)
    target_path = args.target_path
    target_path = os.path.join(target_path, arch)
    compiler_bug_path = args.compiler_bug_path
    compiler_bug_path = os.path.join(compiler_bug_path, arch)
    num_programs = args.num_programs

    list_of_programs_expected = [ "program_{:05d}".format(i) for i in range(num_programs) ]

    for p4c_version in docker_p4c_versions:
        curr_target_path = os.path.join(target_path, p4c_version)
        curr_compiler_bug_path = os.path.join(compiler_bug_path, p4c_version)
        os.makedirs(curr_compiler_bug_path, exist_ok=True)

        list_of_programs_in_curr_target_path = sorted(os.listdir(curr_target_path))
        list_of_programs_in_curr_target_path_short = [ prog.split("-")[0] for prog in list_of_programs_in_curr_target_path ]
        missing_programs = set(list_of_programs_expected) ^ set(list_of_programs_in_curr_target_path_short)
        
        for prog in list(missing_programs):
            prog_name = prog + ".p4"
            file_to_copy_src_path = os.path.join(instrumented_path, prog_name)
            file_to_copy_dst_path = os.path.join(curr_compiler_bug_path, prog_name)
            print("Copying...", file_to_copy_src_path, "to", file_to_copy_dst_path)
            shutil.copyfile(file_to_copy_src_path, file_to_copy_dst_path)


if __name__ == '__main__':
    main()
