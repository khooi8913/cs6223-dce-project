# cs6223-dce-project

## Program Generation
Example usage:
```
python3 generate_program.py --arch top --output-path ./generated/ --instrumented-path ./instrumented --num-programs 100
python3 get_frontend_last.py --arch top --target-path instrumented/
python3 find_differences.py --target-path ./output/
```

## TODO
Automated flow that only keeps "interesting" cases?