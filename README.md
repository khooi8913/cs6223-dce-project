# cs6223-dce-project

## Program Generation
Example usage:
```
python3 generate_program.py --arch top --output-path ./generated/ --instrumented-path ./instrumented --num-programs 100
python3 get_frontend_last.py --arch top --target-path instrumented/
python3 find_differences.py --target-path ./output/
python3 get_compiler_bugs.py --arch top --target-path ./output/ --compiler-bug-path ./compiler_bug/ --num-programs 10000
python3 get_all_passes.py --arch --top --target-path instrument/ --output-path output-end/
```

## TODO
1. Automated flow that only keeps "interesting" cases?
2. Use containerized p4bludgeon and p4c for program generation