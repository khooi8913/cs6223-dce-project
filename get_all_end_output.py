import os
import subprocess
import argparse
from threading import Thread
from multiprocessing import Process

from pprint import pprint

P4C_PATH = os.environ['P4C_PATH'] 
P4C_BUILD_PATH = os.path.join(P4C_PATH, "build")
P4TEST_PATH = os.path.join(P4C_BUILD_PATH, "p4test")
P4C_BM2_PATH = os.path.join(P4C_BUILD_PATH, "p4c-bm2-ss")

# p4lang/p4c container versions
docker_p4c_versions = ["stable", "1.2.4.3", "1.2.4.4", "1.2.4.5", "1.2.3.0", "1.2.3.9"]

# p4test --dump /tmp --top4 FrontEndLast program_000.p4

assert os.path.exists(P4TEST_PATH) and os.path.exists(P4C_BM2_PATH)

def threading_function(arch, p4c_version, target_path, output_path):
    curr_output_path = os.path.join(output_path, p4c_version)
    os.makedirs(curr_output_path, exist_ok=True)
    
    print("==>Current output", curr_output_path)
    list_of_programs_in_curr_output_path = sorted(os.listdir(curr_output_path))
    list_of_programs_in_curr_output_path = [ p.split("-")[0] for p in list_of_programs_in_curr_output_path ]

    list_of_programs = sorted(os.listdir(target_path))
    for prog in list_of_programs:
        prog_name = prog.split(".")[0]
        curr_target_path = os.path.join(target_path, prog)
        if prog_name in list_of_programs_in_curr_output_path:
            continue
        curr_p4_prog_output_path = os.path.join(curr_output_path, prog_name)
        os.makedirs(curr_p4_prog_output_path, exist_ok=True)
        # execute_docker_p4c_commands(arch, p4c_version, curr_target_path, curr_output_path)
        execute_docker_p4c_commands(arch, p4c_version, curr_target_path, curr_p4_prog_output_path)

def execute_docker_p4c_commands(arch, p4c_version, target_path, output_path):
    if arch == "top":
        command = " ".join(["docker run -it -v $(pwd):/p4c p4lang/p4c:"+ p4c_version, "p4test --dump", output_path, "--top4 End", target_path])
    if arch == "v1model":
        command = " ".join(["docker run -it -v $(pwd):/p4c p4lang/p4c:"+ p4c_version, "p4c-bm2-ss --dump", output_path, "--top4 End", target_path])
    if arch == "tna":
        print("Support for TNA not implemented for now.")
        exit(1)
    ret_val, output = subprocess.getstatusoutput(command)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--arch', type=str, default='top',
        choices=['top', 'tna', 'v1model'],
        help='target architecture for the generated p4 program'
    )

    parser.add_argument(
        '--target-path', default='./instrumented/',
        help='target path for the instrumented p4 programs'
    )

    parser.add_argument(
        '--output-path', default='./output-end/',
        help='output path for the IRs'
    )

    args = parser.parse_args()
    pprint(args)
    
    arch = args.arch
    target_path = args.target_path
    target_path = os.path.join(target_path, arch)
    output_path = args.output_path
    output_path = os.path.join(output_path, arch)

    assert os.path.exists(target_path)
    
    threads = []
    for p4c_version in docker_p4c_versions:
        # threads.append(Thread=threading_function, args=(arch, p4c_version, target_path, output_path))
        threads.append(Process(target=threading_function, args=(arch, p4c_version, target_path, output_path)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        # curr_output_path = os.path.join(output_path, p4c_version)
        # os.makedirs(curr_output_path, exist_ok=True)
        
        # print("==>Current output", curr_output_path)
        # list_of_programs_in_curr_output_path = sorted(os.listdir(curr_output_path))
        # list_of_programs_in_curr_output_path = [ p.split("-")[0] for p in list_of_programs_in_curr_output_path ]

        # list_of_programs = sorted(os.listdir(target_path))
        # for prog in list_of_programs:
        #     prog_name = prog.split(".")[0]
        #     curr_target_path = os.path.join(target_path, prog)
        #     if prog_name in list_of_programs_in_curr_output_path:
        #         continue
        #     curr_p4_prog_output_path = os.path.join(curr_output_path, prog_name)
        #     os.makedirs(curr_p4_prog_output_path, exist_ok=True)
        #     # execute_docker_p4c_commands(arch, p4c_version, curr_target_path, curr_output_path)
        #     execute_docker_p4c_commands(arch, p4c_version, curr_target_path, curr_p4_prog_output_path)
        
if __name__ == '__main__':
    main()