import subprocess
import random as rd
import string
from simpleeval import *
import ast
import concurrent.futures
import math
import sys

RAND_SPACE = False
RAND_COMMENT = False

curr_calc = None

def custom_div(a, b):
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    
    result = a / b
    
    if result >= 0:
        return math.floor(result)  # Floor for positive results
    else:
        return math.ceil(result)   # Ceiling for negative results

def rand_id(existing):
    while True:
        name = rd.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        len = rd.randint(1, 5)
        for _ in range(len-1):
            name += rd.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789")
        if name not in existing:
            return name

def rand_num():
    out = rd.randint(-2**10, 2**10-1)
    return '(' + str(out) + ')' if out < 0 else str(out)

def rand_space(max_space=5):
    return ' ' * rd.randint(0, max_space) if RAND_SPACE else ' '

def rand_comment():
    if not RAND_COMMENT:
        return ""
    out = ""
    comment_num = rd.randint(0, 5)
    for _ in range(comment_num):
        characters = string.ascii_letters + string.digits
        len = rd.randint(1, 5)
        out += "--" + "".join(rd.choice(characters) for _ in range(len)) + "\n"
    return out

def gen_calc(file, calc_lines, max_formula_len=5):
    global curr_calc

    out = ""
    avail_ids = dict()

    file.write(rand_comment())

    j = 0
    while j < calc_lines:
        last_avail_ids = avail_ids.copy()

        is_first_round = avail_ids == {}

        # Get new id
        if rd.choice([True, False]) if not is_first_round else True:
            avail_ids[rand_id(avail_ids.keys())] = None

        # Gen formula
        lhs = rd.choice(list(avail_ids.keys()))
        
        rhs = ''
        rhs_calc = ''
        rhs_len = rd.randint(1, max_formula_len)
        # Select paranthesis pos
        lparan = []
        rparan = []
        paran_num = rd.randint(0, rhs_len)
        for _ in range(paran_num):
            lparan.append(rd.randint(0, rhs_len-1))
            rparan.append(rd.randint(lparan[-1]+1, rhs_len))
        lparan.sort()
        rparan.sort()
        lparan.append(-1)
        rparan.append(-1)
        for i in range(rhs_len):
            rhs += rand_space()

            # Write lparan
            if lparan != []:
                while i == lparan[0]:
                    rhs += '('
                    rhs_calc += '('
                    lparan.pop(0)

            rhs += rand_space()

            # Write id or num
            use_id = rd.choice([True, False]) if not is_first_round else False
            if use_id:
                while True:
                    appendix = rd.choice(list(avail_ids.keys()))
                    if avail_ids[appendix]:
                        break
                rhs += appendix
                rhs_calc += str(avail_ids[appendix])
            else:
                appendix = rand_num()
                rhs += appendix
                rhs_calc += appendix

            rhs += rand_space()

            # Write rparan
            if rparan != []:
                while i + 1 == rparan[0]:
                    rhs += ')'
                    rhs_calc += ')'
                    rparan.pop(0)

            rhs += rand_space()

            # Write OP
            if i != rhs_len-1:
                rhs += rd.choice("+-*/")
                rhs_calc += rhs[-1]
                # if rhs[-1] == '/':
                #     rhs_calc += '/'

        rhs += rand_space()

        try:
            curr_calc = rhs_calc
            result = s.eval(rhs_calc)
        except ZeroDivisionError:
            # print("Zero division error!")
            avail_ids = last_avail_ids.copy()
            continue

        # Limit check
        if result < -2**20 or result > 2**20-1 or not float(result).is_integer():
            # print("Limit error!")
            avail_ids = last_avail_ids.copy()
            continue

        avail_ids[lhs] = int(result)
        file.write(f"{lhs} := {rhs};\n")
        file.write(f"write({lhs});\n")
        out += str(avail_ids[lhs]) + '\n'
        file.write(rand_comment())

        j += 1

    out = out[:-1]
    return out

def gen_test():
    with open("auto_test.m", "w") as p:
        p.write("begin\n")
        expect_out = gen_calc(p, 2)
        p.write("end\n")
    return expect_out

def run_test():
    process = subprocess.Popen(["bash", "run.sh", "./auto_test.m"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    complete_out = stdout.decode()
    enter_pos = complete_out.find('\n')
    out = complete_out[enter_pos+1:-1]
    return out, stderr

def error():
    import shutil
    shutil.copyfile("auto_test.m", "error_test.m")
    exit(1)

TIMEOUT_THRESHOLD = 2  # Timeout threshold in seconds

def run_test_with_timeout():
    expect_out = gen_test()
    out, err = run_test()
    return expect_out, out, err

if __name__ == "__main__":
    start_loop = 0
    total_loop = 0
    if len(sys.argv) == 1:
        print("An argument is required: Total Loop.")
        exit()
    elif len(sys.argv) == 2:
        total_loop = int(sys.argv[1])
    elif len(sys.argv) == 3:
        start_loop = int(sys.argv[1])
        total_loop = int(sys.argv[2])
    else:
        print("Too many argument!")

    for i in range(start_loop, total_loop):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            s = SimpleEval()
            s.operators[ast.Div] = custom_div
            future = executor.submit(run_test_with_timeout)
            try:
                expect_out, out, err = future.result(timeout=TIMEOUT_THRESHOLD)
                if expect_out != out:
                    print(f"Error at test {i}! Expect '{expect_out}', got '{out}'.")
                    error()
                if err != b'':
                    print(f"Error at test {i}! Got err '{err}'.")
                    error()
                print(f"Done case {i}")
            except concurrent.futures.TimeoutError:
                print(f"Timeout at test {i}, rerunning...")
                new_tester = subprocess.run(["python", "tester.py", str(i), str(total_loop)])
                i -= 1

    print("All test passed!")