# micro_compiler_tester
This is a tester of compiler in Micro language. The program can generate testcases in Micro to test:
1. Assignment Operations
2. Arithmetic Calculations
3. Variable Namings
4. Writing Functionalities
5. Comment Line Logics

TODO: READ

This project uses ![simpleeval](https://github.com/danthedeckie/simpleeval) - an open-source eval-ing program for custom division operators. Strangely, the evaluation process sometimes crashs and spit out a "Killed" without any errors. This project ignores this error and keeps running.

## How to run
This project is only tested on Linux x86-64 system simulating riscv with qemu-riscv.

1. Rename your compiler executable to "compiler".
2. Modify the CALL process in run.sh.