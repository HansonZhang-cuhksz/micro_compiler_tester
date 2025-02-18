#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <input_file> [--png | -p]"
  exit 1
fi

INPUT_FILE=$1
GENERATE_PNG=false

# Check if the --png or -p flag is provided
if [ "$2" == "--png" ] || [ "$2" == "-p" ]; then
  GENERATE_PNG=true
fi

./compiler "$INPUT_FILE"
if [ "$GENERATE_PNG" = true ]; then
  dot -Tpng ./ast.dot -o ./ast.png
fi

opt ./program.ll -S --O3 -o ./program_optimized.ll
llc -march=riscv64 ./program_optimized.ll -o ./program.s
riscv64-unknown-linux-gnu-gcc ./program.s -o ./program
qemu-riscv64 -L /opt/riscv/sysroot ./program