# -*- coding: utf-8 -*-
import time
import re

def is_number(str):
    if str == "true" or str == "false":
        return True
    try:
        float(str)
        return True
    except:
        return False
 
def is_name(str):
    return re.match("\w+", str)

def peek(stack):
    return stack[-1] if stack else None

def greater_precedence(op1, op2):
    precedences = {'=' : 0, '+' : 3, '-' : 3, '*' : 5, '/' : 5, '!' : 2, '!=' : 1, '>' : 1, '<' : 1, '>=' : 1, '<=' : 1, '!=' : 1, '==' : 1, '&' : 4, '^' : 4, '|' : 4, '&&' : 2, '||' : 2, '^^' : 2, '++' : 6, '--' : 6, '+=' : 0, '-=' : 0, '*=' : 0, '/=' : 0}
    return precedences[op1] > precedences[op2]

_arg_ = 0 # function parameters
_var_ = 1 # function variables
_ret_ = 2 # function internal variables (kinda like registers)
_prog_ = 3 # function actual code
_rtrck_ = 4 # keep track of which internal variables are used (to remove them later, only used at compile time)

_v_ret_ = '#'
_v_var_ = '@'
_v_arg_ = '$'
_v_res_ = '~'

gl_func = {"print": 1, "if": 1, "else": 0, "elif": 1, "endif": 0, "while": 1, "for": 3, "return": 1}
lc_func = {}
program = {"": [[], [], [], [], []]} # "" is the main function
scope = "" # current function selected

def is_func(str):
    if str in lc_func or str in gl_func:
        return True
    return False

def is_op(str):
    list = {'=', '+', '-', '*', '/', '!', '!=', '>', '<', '>=', '<=', '!=', '==', '&', '^', '|', '&&', '||', '^^', '++', '--', '+=', '-=', '*=', '/='}
    if str in list:
        return True
    return False

def is_single_op(str):
    list = {'!', '++', '--'}
    if str in list:
        return True
    return False

def is_equal_op(str):
    list = {'=', '+=', '-=', '*=', '/='}
    if str in list:
        return True
    return False

def is_other_op(str):
    list = {'+', '-', '*', '/', '!=', '>', '<', '>=', '<=', '!=', '==', '&', '^', '|', '&&', '||', '^^'}
    if str in list:
        return True
    return False

def is_param(str):
    if str in program[scope][_arg_]:
        return True
    return False

def is_variable(str):
    if str in program[scope][_var_]:
        return True
    return False

def is_string(str):
    if len(str) >= 2 and str[0] == '"' and str[-1]== '"':
        return True
    return False

def is_result(str):
    if len(str) < 2 or not str[1:].isdigit():
        return False
    if str[0] != _v_ret_:
        return False
    if int(str[1:]) >= len(program[scope][_ret_]):
        return False
    return True

def get_result_id(str):
    if len(str) < 2 or not str[1:].isdigit():
        return -1
    if str[0] != _v_ret_ and str[0] != _v_res_:
        return -1
    tmp = int(str[1:])
    if tmp >= len(program[scope][_ret_]):
        return -1
    return int(tmp)

def is_usable_var(str):
    if len(str) < 2 or not str[1:].isdigit():
        return False
    if str[0] != _v_var_ and str[0] != _v_arg_:
        return False
    tmp = int(str[1:])
    if str[0] == _v_var_ and tmp >= len(program[scope][_var_]):
        return False
    elif str[0] == _v_arg_ and tmp >= len(program[scope][_arg_]):
        return False
    return True

def is_var(str):
    if len(str) < 2 or not str[1:].isdigit():
        return False
    if str[0] != _v_var_:
        return False
    if int(str[1:]) >= len(program[scope][_var_]):
        return False
    return True

def get_var_id(str):
    if len(str) < 2 or not str[1:].isdigit():
        return -1
    if str[0] != _v_var_:
        return -1
    tmp = int(str[1:])
    if tmp >= len(program[scope][_var_]):
        return -1
    return int(tmp)

def var_check(str):
    if len(str) < 2 or not str[1:].isdigit():
        return False
    if str[0] != _v_ret_ and str[0] != _v_var_ and str[0] != _v_arg_:
        return False
    tmp = int(str[1:])
    if str[0] == _v_ret_ and tmp >= len(program[scope][_prog_]):
        return False
    elif str[0] == _v_var_ and tmp >= len(program[scope][_var_]):
        return False
    elif str[0] == _v_arg_ and tmp >= len(program[scope][_arg_]):
        return False
    return True

def update_ret_var(value, result):
    if is_result(value):
        id = get_result_id(value)
        if id >= len(program[scope][_ret_]) and program[scope][_ret_][id] == -1:
            return False
        r = _v_res_+str(id)
        if result[program[scope][_ret_][id]][-1] != r:
            result[program[scope][_ret_][id]].append(r)
        program[scope][_ret_][id] = -1
        program[scope][_rtrck_][id] = True
    return True

def new_ret_var(line):
    for i in range(0, len(program[scope][_ret_])):
        if program[scope][_ret_][i] == -1:
            program[scope][_ret_][i] = line
            return i
    program[scope][_ret_].append(line)
    program[scope][_rtrck_].append(False)
    return len(program[scope][_ret_])-1

def lock_var(id, line):
    if id >= len(program[scope][_ret_]) or program[scope][_ret_][id] != -1:
        return False
    program[scope][_ret_][id] = line
    return True

def unlock_var(id):
    if id >= len(program[scope][_ret_]) or program[scope][_ret_][id] == -1:
        return False
    program[scope][_ret_][id] = -1
    return True

def reset_ret_var():
    global program
    for i in range(0, len(program[scope][_ret_])):
        program[scope][_ret_][i] = -1

def is_ret_var(str):
    if len(str) < 2 or not str[1:].isdigit():
        return False
    if str[0] != _v_res_:
        return False
    if int(str[1:]) >= len(program[scope][_ret_]):
        return False
    return True

def has_ret_var(line):
    if len(line) < 2:
        return False
    return is_ret_var(line[-1])

def apply_operator(operators, values, result):
    op = operators.pop()
    rid = new_ret_var(len(result))
    if is_op(op):
        right = values.pop()
        if is_single_op(op):
            if not update_ret_var(right, result):
                return False
            result.append([op, right])
        else:
            left = values.pop()
            if not update_ret_var(right, result) or not update_ret_var(left, result):
                return False
            result.append([op, left, right])
    elif is_func(op):
        if op in gl_func: narg = gl_func[op]
        else: narg = lc_func[op]
        result.append([])
        for i in range(0, narg):
            v = values.pop()
            if not update_ret_var(v, result):
                return False
            result[-1].append(v)
        result[-1].append(op)
        result[-1].reverse()
    else:
        return False
    values.append(_v_ret_+str(rid))
    return True

def evaluate(expression):
    global program
    tokens = re.findall("(?:\"[^\"]*\")|\+=|-=|\*=|/=|==|>=|<=|!=|\+\+|--|(?:[-]?\d+\.\d+)|(?:[-]?\d+)|[+=\,/.*()!><-]|\w+", expression) # search for the various words
    if len(tokens) == 0:
        return True
    values = []
    operators = []
    result = []
    reset_ret_var()
    for token in tokens:
        if is_number(token): # value, push into the value stack
            values.append(token)
        elif is_string(token): # same, but string
            values.append(token)
        elif token == '.':
            print "What's this dot?"
            return False
        elif token == '(': # left bracket, push into the operator stack
            operators.append(token)
        elif token == ')': # right bracket
            top = peek(operators)
            while top is not None and top != '(': # while the top operator isn't the left bracket
                # error check
                if not operators or len(values) < 1 or (not is_op(peek(operators)) and not is_func(peek(operators))):
                    print "There is a bracket problem"
                    return False
                if not apply_operator(operators, values, result): # empty the operator stack
                    print "Operator error, failed to build the instruction"
                    return False
                top = peek(operators)
            operators.pop() # discard the left bracket
            if is_func(peek(operators)):
                if not apply_operator(operators, values, result):
                    print "Operator error, failed to build the instruction"
                    return False
        elif token == ',': # comma
            while peek(operators) is not None and peek(operators) != '(':
                if is_op(peek(operators)):
                    if not apply_operator(operators, values, result):
                        print "Operator error, failed to build the instruction"
                        return False
                else:
                    values.append(operators.pop())
            if not operators:
                print "There is a comma problem"
                return False
        elif is_name(token): # word
            if is_func(token):
                operators.append(token)
            else:
                if is_param(token):
                    values.append(_v_arg_+str(program[scope][_arg_].index(token)))
                elif not is_variable(token):
                    if token[0].isdigit():
                        print "You can't put a number at the start of your variable name"
                        return False
                    program[scope][_var_].append(token)
                    values.append(_v_var_+str(program[scope][_var_].index(token)))
                elif is_variable(token):
                    values.append(_v_var_+str(program[scope][_var_].index(token)))
                else:
                    values.append(token)
        else: # operator
            top = peek(operators)
            while top is not None and top not in "()" and greater_precedence(top, token):
                if not operators or len(values) < 1:
                    print "Something weird happened"
                    return False
                if not apply_operator(operators, values, result):
                    print "Operator error, failed to build the instruction"
                    return False
                top = peek(operators)
            operators.append(token)
    # empty the operator stack
    while peek(operators) is not None:
        if not operators or len(values) < 2: return False
        if not apply_operator(operators, values, result):
            print "Operator error, failed to build the instruction"
            return False
    if len(values) != 1:
        print "Unexpected end of the line"
        return False
    # save the code
    for r in result:
        program[scope][_prog_].append(r)
    return True

def define(tokens, str): # assume the tokens have been tested to some extent before
    global lc_func
    global scope
    if is_func(tokens[1]): # check if the function name already exists
        print "Function name", tokens[1], "already exists"
        return False
    param = [] # temp parameter array
    if len(tokens) > 6: # if there is a chance of having a parameter
        fpara = tokens[3:-1] # remove the beginning and the end (because not needed, we could actually slice more)
        for i in range(0, len(fpara)):
            if i % 2 == 0: # if even, it must be a variable name OR the closing bracket if no parameters)
                if fpara[i] == ')' and len(param) == 0:
                    break # end of the loop if the bracket is found
                if not is_name(fpara[i]):
                    print fpara[i], "isn't a valid name"
                    return False # error if not
                param.append(fpara[i])
            elif i % 2 == 1: # if odd, it must be a comma or the closing bracket
                if fpara[i] != ',' and fpara[i] != ')':
                    print "Expected a comma or the closing bracket"
                    return False # error if not
                elif fpara[i]== ')':
                    break # end of the loop if the bracket is found
    elif len(tokens) < 4 or tokens[3] != ')': # check the bracket isn't missing (here we are assuming an empty function, no parameter)
        print "Invalid declaration, something is missing"
        return False

    str = str.split(')', 1) # retrieve the second part of the string, the one between { }
    if len(str) < 2: # check the split is correct
        return False
    str = str[1].strip().lstrip() # strip whitespaces
    if len(str) < 2 or str[0] != '{' or str[-1] != '}': # check everything is correct still
        return False
    str = str[1:-1] # remove { }

    lc_func[tokens[1]] = len(param) # add the function name to our dictionary
    scope = tokens[1] # change the current scope
    program[scope] = [[], [], [], [], []] # create the array to hold the function
    program[scope][_arg_] = param
    r = process(str, True) # process
    scope = "" # switch back to the main scope
    return r

def process(cmd, sub=False):
    global scope
    str = ""
    scp = 0
    isstr = False
    escape = False
    comment = 0
    for c in cmd: # process each char
        # comment mode
        if comment == 1:
            if c == '/':
                comment = 2
                continue
            if c == '*':
                comment = 3
                continue
            str += '/'
            comment = 0
        elif comment == 2:
            if c == '\n':
                comment = 0
            continue
        elif comment > 2:
            if (comment-3)%3 == 0:
                if c == '*':
                    comment += 1
                elif c == '/':
                    comment += 2
                continue
            elif (comment-3)%3 == 1:
                if c == '/':
                    comment -=4
                elif c != '*':
                    comment -= 1
                continue
            elif (comment-3)%3 == 2:
                if c == '*':
                    comment += 1
                elif c != '/':
                    comment -= 2
                continue
        # normal mode
        if c == '{' and not isstr and not escape: # count nested {} blocks
            scp += 1
            str += c
        elif c == '}' and not isstr and not escape:
            scp -= 1
            str += c
            if scp < 0: # it shouldn't go negative
                print "Invalid }"
                return False
        elif c == '"' and not escape: # "string" mode
            isstr = not isstr
            str += c
        elif c == '/' and not isstr and not escape:
            comment = 1
            continue
        elif c == '\\' and not escape: # escape character
            escape = True
        elif c == ';' and scp == 0 and not isstr and not escape: # end of a line
            tokens = re.findall("def|[\(\),]|\w+", str) # check for a function declaration
            if len(tokens) < 4 or tokens[0] != 'def' or not is_name(tokens[1]) or tokens[2] != '(': # not a declaration
                if not evaluate(str): # we evaluate
                    print "Syntax error:", str
                    return False
            elif scope != "" or scp != 0 or escape or isstr: # it's a declaration
                print "Bad function declaration:", str # error happened
                return False
            elif not define(tokens, str):
                print "Error in function:", scope
                return False
            str = ""
        else: # regular character
            str += c
            escape = False # disable the escape

    # final error check
    if (not sub and scope != "") or scp != 0 or escape or isstr or (not str.isspace() and str != ""):
        print "unexpected end of the script"
        return False

    return True

def error_check():
    global scope
    print "*** Error check ***"
    for f in program:
        func = program[f]
        if f != "":
            print "checking function", f, "..."
        else:
            print "checking main..."
        scope = f
        var_count = [0]*len(func[_var_])
        for l in func[_prog_]:
            for i in range(1, len(l)):
                if is_var(l[i]):
                    var_count[get_var_id(l[i])] += 1
            if is_op(l[0]):
                if (l[0] == '=' and (len(l) < 3 or len(l) > 4)) or (is_single_op(l[0]) and len(l) != 2) or (not is_single_op(l[0]) and l[0] != '=' and len(l) != 3):
                    print "Line", l,": invalid operation"
                    return False
                for i in range(1, len(l)):
                    if not var_check(l[i]) and not is_number(l[i]) and not is_string(l[i]):
                        print "Line", l,": invalid variable", l[i]
                        return False
            elif is_func(l[0]):
                if l[0] in gl_func:
                    count = gl_func[l[0]]
                else:
                    count = lc_func[l[0]]
                if len(l) != count + 1:
                    return False
        for v in var_count:
            if v == 0:
                print "Unused variable name '" + str(func[_var_][var_count.index(v)]) + "', mistyped function name?"
                return False
    return True

def optimize():
    global program
    global scope
    print "*** Optimization ***"
    for f in program:
        func = program[f]
        scope = f
        # first pass
        reset_ret_var()
        for i in range(0, len(func[_prog_])):
            l = func[_prog_][i]
            for j in range(1, len(l)): # take note of the used return variables
                if is_ret_var(l[j]):
                    id = get_result_id(l[j])
                    func[_ret_][id] = i
            if is_other_op(l[0]) and not has_ret_var(l) and not is_usable_var(l[1]): # remove the instructions not storing their results anywhere
                func[_prog_][i] = None
                continue
            elif is_equal_op(l[0]) and not has_ret_var(l) and is_usable_var(l[1]) and is_result(l[2]): # remove equal instructions storing their results in a variable. updating the previous line.
                id = get_result_id(l[2])
                line = func[_ret_][id]
                line = func[_prog_][line]
                if not has_ret_var(line):
                    return False
                line[-1] = l[1]
                func[_ret_][id] = -1
                func[_prog_][i] = None
                continue
            for j in range(1, len(l)):
                if is_result(l[j]):
                    id = get_result_id(l[j])
                    func[_ret_][id] = -1
        # delete None lines
        h = 0
        while h < len(func[_prog_]):
            if func[_prog_][h] == None:
                del func[_prog_][h]
            else:
                h += 1
    return True

def print_func():
    func = program[scope]
    if scope == "":
        print "-> Main function"
    else:
        print "\n-> Function '"+scope+"'"
    print len(func[_arg_]), "parameter(s), ", func[_arg_]
    print "Local variable list:", func[_var_]
    print len(func[_ret_]), "internal variable(s)"
    for i in range(0, len(func[_prog_])):
        print str(i).zfill(3) + ":", str(func[_prog_][i])

def print_program():
    global scope
    print "*** Program Content ***"
    for f in program:
        scope = f
        print_func()

def compile(cmd):
    global lc_func
    global program
    global scope
    lc_func = {}
    program = {"": [[], [], [], [], []]}
    scope = ""

    print "*** Compilation ***"
    try:
        start_time = time.time()
        if not process(cmd):
            return False
        print("Done: %s seconds\n" % (time.time() - start_time))
        #print_program()
        start_time = time.time()
        if not optimize():
            return False
        print("Done: %s seconds\n" % (time.time() - start_time))
        """print("Done: %s seconds\n" % (time.time() - start_time))
        start_time = time.time()
        if not error_check():
            return False
        print("Done: %s seconds\n" % (time.time() - start_time))"""
        print_program()
    except Exception, e:
        print "Exception:", e
        return False
    return True

return_value = None
def play_func(name, args=[]):
    global return_value
    global scope
    if name not in program:
        print "unknown function", name
        return False
    elif len(args) < len(program[name][_arg_]):
        print "missing argument(s) in", name, "call"
        return False
    elif len(args) > len(program[name][_arg_]):
        print "too many argument(s) in", name, "call"
        return False
    prev_scp = scope
    scope = name
    for l in program[scope][_prog_]:
        if l[0] in lc_func:
            ret = play_func(l[0], l[1:])
            if not ret:
                print "call stack:", l
        elif l[0] in gl_func:
            if l[0] == "print" and len(l) == 2:
                print l[1]
        elif is_op(l[0]):
            pass
    scope = prev_scp
    return True

def play():
    print "*** Run ***"
    start_time = time.time()
    r = play_func("")
    print "Returned", r
    print("Done: %s seconds\n" % (time.time() - start_time))

# TO DO LIST
# - REDO ERROR CHECK
# - remove unused internal variables
# - remove unused local variables
# - add loop and conditions
# - add arrays
# -??

with open('test.txt', 'r') as myfile:
    data=myfile.read()
if compile(data):
    play()
else:
    print "Compilation returned an error"