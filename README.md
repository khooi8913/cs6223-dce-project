# cs6223-dce-project

This repository holds the implementation for the tools used in evaluating the feasibility of applying the techniques proposed in the [DCE paper](https://dl.acm.org/doi/10.1145/3503222.3507764) for C compilers on the P4 compiler.
> Note:
> The script hard codes P4C container versions stable, 1.2.3.0, 1.2.3.9, 1.2.4.3, 1.2.4.4 and 1.2.4.5.
> They should be in the form of p4lang/p4c:<version>, e.g., p4lang/p4c:stable.
> You can modify the versions to compare easily in the code (it is in a list).
> To build the Docker images of the P4C, make sure to do it from the cloned repo, and DO NOT use the release tarball/ ZIPs.

## Usage

We assume that you have cloned the [p4c](https://github.com/p4lang/p4c) repository, e.g., on your home directory, and compile and install it together with the random P4 code generator, [p4bludgeon](https://github.com/p4gauntlet/bludgeon).

Then, before executing the following scripts, make sure to export the path to the P4C.
```
export P4C_PATH=/path/to/p4c
```

### Step 1: Program Generation
```
python3 generate_program.py --arch top --output-path ./generated/ --instrumented-path ./instrumented --num-programs 100
```
### Step 2: Compile the Generated Programs and Dump the FrontEnd IRs (--top4 FrontEndLast)
```
python3 get_frontend_last.py --arch top --target-path instrumented/
```
### Step 3: Compare the FrontEnd IRs (to find interesting cases)
```
python3 find_differences.py --target-path ./output/
```
### Step 4: Get List of Programs with Compiler Bugs
```
python3 get_compiler_bugs.py --arch top --target-path ./output/ --compiler-bug-path ./compiler_bug/ --num-programs 10000
```
### Step 5: Compile the Generated Programs (again) and Dump all IRs (--top4 End)
```
python3 get_all_end_output.py --arch top --target-path instrumented/ --output-path output-end/
```
### Step 6: Further Analyze Programs that are of Interest (based on the report generated from Step 3)
```
python3 inspect_all_passes.py --arch top --program-name program_06725 --p4c-ver-1 1.2.4.5 --p4c-ver-2 stable
```

## TODO
1. Automated flow that only keeps "interesting" cases?
2. Use containerized p4bludgeon and p4c for program generation
3. Add command line option for P4C versions?
4. Optimize flow to prevent redundant compilations (i.e., Step 3 and Step 5) to speed up the flow
5. Implement automatic analysis and do git bisect?
6. Automatically build P4C Docker images?