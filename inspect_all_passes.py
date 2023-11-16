import os
import re
import argparse
from pprint import pprint
from natsort import natsorted

docker_p4c_versions = ["stable", "1.2.4.3", "1.2.4.4", "1.2.4.5", "1.2.3.0", "1.2.3.9"]

def find_markers(p4_code):
    pattern = r'marker_dce\d{2}\(\);'
    # Extracting dce markers from the P4 code
    markers = re.findall(pattern, p4_code)

    # Printing the extracted markers
    # for marker in markers:
    #     print(marker)
    return sorted(markers)

def get_list_of_programs(output_path):
    list_of_p4_programs = sorted(os.listdir(output_path))
    list_of_p4_programs_short = [ p.split("-")[0] for p in list_of_p4_programs ]
    # print(list_of_p4_programs)
    return list_of_p4_programs, list_of_p4_programs_short

def find_item_idx_from_list_if_match(input_list, match_condition):
    for idx, element in enumerate(input_list):
        if element == match_condition:
            return idx
    return -1

def compare_frontend_ir(target_path, p4c_version1, p4c_version2):
    res = dict()
    p4c_version1_path = os.path.join(target_path, p4c_version1)
    p4c_version2_path = os.path.join(target_path, p4c_version2)
    list_of_p4_programs_1, list_of_p4_programs_1_short = get_list_of_programs(p4c_version1_path)
    list_of_p4_programs_2, list_of_p4_programs_2_short = get_list_of_programs(p4c_version2_path)

    missing_p4_programs_short = set(list_of_p4_programs_1_short) ^ set(list_of_p4_programs_2_short)
    common_p4_programs_short = list(set(list_of_p4_programs_1_short) & set(list_of_p4_programs_2_short))

    for prog in common_p4_programs_short:
        # p4_prog_1_path = os.path.join(p4c_version1_path, list_of_p4_programs_1[idx])
        # p4_prog_2_path = os.path.join(p4c_version2_path, list_of_p4_programs_2[idx])
        prog_1_idx = find_item_idx_from_list_if_match(list_of_p4_programs_1_short, prog)
        prog_2_idx = find_item_idx_from_list_if_match(list_of_p4_programs_2_short, prog)
        assert prog_1_idx != -1 and prog_2_idx != -1
        p4_prog_1_path = os.path.join(p4c_version1_path, list_of_p4_programs_1[prog_1_idx])
        p4_prog_2_path = os.path.join(p4c_version2_path, list_of_p4_programs_2[prog_2_idx])
        p4_prog_1 = ""
        p4_prog_2 = ""
        with open(p4_prog_1_path) as f:
            p4_prog_1 = f.read()
        with open(p4_prog_2_path) as f:
            p4_prog_2 = f.read()
        # Regular expression pattern to match the specified pattern
        pattern = r'extern void marker_dce\d{2}\(\);'

        # Remove the pattern from the text
        p4_prog_1 = re.sub(pattern, '', p4_prog_1)
        p4_prog_2 = re.sub(pattern, '', p4_prog_2)

        p4_prog_1_markers = find_markers(p4_prog_1)
        p4_prog_2_markers = find_markers(p4_prog_2)

        in_1_but_not_2 = [ x for x in p4_prog_1_markers if x not in p4_prog_2_markers]
        # in_2_but_not_1 = [ x for x in p4_prog_2_markers if x not in p4_prog_1_markers]
        # print(prog)
        # print("in 1 but not 2", in_1_but_not_2)
        res[prog] = len(in_1_but_not_2)
        # print("in 2 but not 1", in_2_but_not_1)
    return res

def write_report(program_name, report_path, p4c_version1, p4c_version2, result):
    report_name = p4c_version1 + "-" + p4c_version2
    curr_report_path = os.path.join(report_path, report_name)
    os.makedirs(curr_report_path, exist_ok=True)
    curr_report_file = os.path.join(curr_report_path, program_name)
    with open(curr_report_file, 'w') as f:
        f.write(",count\n")
        for k,v in result.items():
            f.write(k + "," + str(v) + "\n")


def get_frontend_midend_files_and_passes(target_path, p4c_ver_1, program_name):
    p4c_ver_1_path = os.path.join(target_path, p4c_ver_1, program_name)
    p4c_ver_1_files = natsorted(os.listdir(p4c_ver_1_path))
    p4c_ver_1_frontend_files = [ p for p in p4c_ver_1_files if 'FrontEnd' in p ]
    p4c_ver_1_frontend_passes = [ p.split('-')[1].split('_')[2].split(".")[0] for p in p4c_ver_1_frontend_files ]
    p4c_ver_1_midend_files = [ p for p in p4c_ver_1_files if 'MidEnd' in p ]
    p4c_ver_1_midend_passes = [ p.split('-')[1].split('_')[2].split(".")[0] for p in p4c_ver_1_midend_files ]
    assert len(p4c_ver_1_frontend_files) + len(p4c_ver_1_midend_files) == len(p4c_ver_1_files)
    return p4c_ver_1_frontend_files, p4c_ver_1_frontend_passes, p4c_ver_1_midend_files, p4c_ver_1_midend_passes

def get_full_filename_if_pass_exit(front_or_midend_pass, list_of_front_or_midend_files):
    for f in list_of_front_or_midend_files:
        if front_or_midend_pass in f:
            return f
    return None

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--arch', type=str, default='top',
        choices=['top', 'tna', 'v1model'],
        help='target architecture for the generated p4 program'
    )

    parser.add_argument(
        '--program-name', default='program_00000',
        help='program to be investigated'
    )

    parser.add_argument(
        '--p4c-ver-1', type=str, required=True,
        choices=docker_p4c_versions,
        help='p4c to compare 1'
    )

    parser.add_argument(
        '--p4c-ver-2', type=str, required=True,
        choices=docker_p4c_versions,
        help='p4c to compare 2'
    )

    parser.add_argument(
        '--target-path', default='./output-end/',
        help='path to directory where the IRs for each compiler version are stored, e.g., output-end/'
    )

    parser.add_argument(
        '--report-path', default='./report-end/',
        help='report path'
    )

    args = parser.parse_args()
    pprint(args)
       
    arch = args.arch
    program_name = args.program_name

    p4c_ver_1 = args.p4c_ver_1
    p4c_ver_2 = args.p4c_ver_2
    assert p4c_ver_1 != p4c_ver_2

    target_path = args.target_path
    target_path = os.path.join(target_path, arch)

    report_path = args.report_path
    report_path = os.path.join(report_path, arch)

    assert os.path.exists(target_path)
    if not os.path.exists(report_path):
        os.makedirs(report_path, exist_ok=True)

    p4c_ver_1_frontend_files, p4c_ver_1_frontend_passes, p4c_ver_1_midend_files, p4c_ver_1_midend_passes = get_frontend_midend_files_and_passes(target_path, p4c_ver_1, program_name)
    p4c_ver_2_frontend_files, p4c_ver_2_frontend_passes, p4c_ver_2_midend_files, p4c_ver_2_midend_passes = get_frontend_midend_files_and_passes(target_path, p4c_ver_2, program_name)

    # TODO: replace with ver2
    common_frontend_passes = set(p4c_ver_1_frontend_passes) & set(p4c_ver_2_frontend_passes)
    common_midend_passes = set(p4c_ver_1_midend_passes) & set(p4c_ver_2_midend_passes) 

    # Use the P4C that has more passes as the reference
    reference_p4c = 1 if len(p4c_ver_1_frontend_passes) + len(p4c_ver_1_midend_passes) >= len(p4c_ver_2_frontend_passes) + len(p4c_ver_2_midend_passes) else 2
    if reference_p4c == 1:
        reference_frontend_passes = p4c_ver_1_frontend_passes
        reference_midend_passes = p4c_ver_1_midend_passes
    else:
        reference_frontend_passes = p4c_ver_2_frontend_passes
        reference_midend_passes = p4c_ver_2_midend_passes

    # Now, iterate through the two compilers, and keep a report
    # Use -1 if a specific pass does not exist for a particular version
    # Example:
    # FrontEnd_XXX,1
    # FrontEnd_XXX,-1
    all_results = dict()
    for fp in reference_frontend_passes:
        p4c_v1_file = get_full_filename_if_pass_exit(fp, p4c_ver_1_frontend_files)
        p4c_v2_file = get_full_filename_if_pass_exit(fp, p4c_ver_2_frontend_files)
        res = -1
        if p4c_v1_file and p4c_v2_file:
            p4c_v1_fp_path = os.path.join(target_path, p4c_ver_1, program_name, p4c_v1_file) 
            p4c_v2_fp_path = os.path.join(target_path, p4c_ver_2, program_name, p4c_v2_file) 
            
            p4_prog_1 = ""
            p4_prog_2 = ""
            with open(p4c_v1_fp_path) as f:
                p4_prog_1 = f.read()
            with open(p4c_v2_fp_path) as f:
                p4_prog_2 = f.read()
            # Regular expression pattern to match the specified pattern
            pattern = r'extern void marker_dce\d{2}\(\);'

            # Remove the pattern from the text
            p4_prog_1 = re.sub(pattern, '', p4_prog_1)
            p4_prog_2 = re.sub(pattern, '', p4_prog_2)

            p4_prog_1_markers = find_markers(p4_prog_1)
            p4_prog_2_markers = find_markers(p4_prog_2)
            in_1_but_not_2 = [ x for x in p4_prog_1_markers if x not in p4_prog_2_markers ]
            res = len(in_1_but_not_2)
        all_results["FrontEnd_" + fp] = res
    
    for mp in reference_midend_passes:
        p4c_v1_file = get_full_filename_if_pass_exit(mp, p4c_ver_1_midend_files)
        p4c_v2_file = get_full_filename_if_pass_exit(mp, p4c_ver_2_midend_files)
        res = -1
        if p4c_v1_file and p4c_v2_file:
            p4c_v1_mp_path = os.path.join(target_path, p4c_ver_1, program_name, p4c_v1_file) 
            p4c_v2_mp_path = os.path.join(target_path, p4c_ver_2, program_name, p4c_v2_file) 
            
            p4_prog_1 = ""
            p4_prog_2 = ""
            with open(p4c_v1_mp_path) as f:
                p4_prog_1 = f.read()
            with open(p4c_v2_mp_path) as f:
                p4_prog_2 = f.read()
            # Regular expression pattern to match the specified pattern
            pattern = r'extern void marker_dce\d{2}\(\);'

            # Remove the pattern from the text
            p4_prog_1 = re.sub(pattern, '', p4_prog_1)
            p4_prog_2 = re.sub(pattern, '', p4_prog_2)

            p4_prog_1_markers = find_markers(p4_prog_1)
            p4_prog_2_markers = find_markers(p4_prog_2)
            in_1_but_not_2 = [ x for x in p4_prog_1_markers if x not in p4_prog_2_markers ]
            res = len(in_1_but_not_2)
        all_results["MidEnd_" + mp] = res
    
    for k,v in all_results.items():
        print(k + "," + str(v))

    write_report(program_name, report_path, p4c_ver_1, p4c_ver_2, all_results)

        
    # for p in p4c_ver_1_frontend_passes:
    #     print(p)
    # for p in p4c_ver_1_midend_passes:
    #     print(p)

    # p4c_ver_1_path = os.path.join(target_path, p4c_ver_1, program_name)

    # for p4c_version1 in docker_p4c_versions:
    #     for p4c_version2 in docker_p4c_versions:
    #         if p4c_version1 == p4c_version2:
    #             continue
    #         print(p4c_version1, p4c_version2)
    #         result = compare_frontend_ir(target_path, p4c_version1, p4c_version2)
    #         result = dict(sorted(result.items(), key=lambda x:x[1], reverse=True))
    #         write_report(report_path, p4c_version1, p4c_version2, result)

if __name__ == '__main__':
    main()