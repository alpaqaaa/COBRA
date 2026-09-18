scopes = [{}] 
object_vars = [] 

functions = { 
# reserving function names 
"NUM": None, 
"STR": None, 
"BOOL": None, 
"SET": None, 
"ADD": None, 
"MOD": None, 
"FLIP": None, 
"CMP": None, 
"IN": None, 
"OUT": None, 
"JMP": None, 
"DEF": None, 
"//": None, 
"": None, 
"ENDDEF": None 
} 

types = { 
"STR": [("String", None)], 
"NUM": [("Number", None)], 
"BOOL": [("Bool", None)] 
} 

# "clear" shell 
def cls(n): 
    print("\n" * n) 

def asplit(index, line): 
    quoted = False 
    idx = 0 
    split_line = [] 
    current = "" 
    while idx < len(line): 
        if line[idx] == '"': 
            quoted = not quoted 
        elif line[idx] == " " and not quoted: 
            split_line.append(current) 
            current = "" 
        else: 
            current += line[idx] 
        idx += 1 
    split_line.append(current) 
    if quoted: 
        raise SyntaxError(str(index) + ': " expected.') 
    return split_line

# make program understand numeric values (or representative variable names) 
def resolve_number(index, num): 
# handling uninitialized vars 
    if num == None: 
        return None 

    if isinstance(num, int):
        return int(num)

    if num[0] == "<": 
        n_idx = 1 
        while n_idx < len(num) and num[n_idx] != ">": 
            n_idx += 1 
        attribute = num[1:n_idx] 
        try: 
            string = num[n_idx+2:] 
        except: 
            raise SyntaxError(str(index) + f"Attribute {attribute} expected parent but never got one.") 

        match attribute: 
            case "LEN": 
                return len(resolve_string(index, string)) 

            case _:
                AttributeError(str(index) + f"Invalid attribute {attribute}.") 

# handling invalid number type error 
    try: 
# check if given input is numeric value 
        int(num) 
    except: 
# if not, reverse scope search to find variable with name equivalent to input 
        for scope in reversed(scopes): 
            if num in scope: 
                return resolve_number(index, scope[num][1]) 

        raise ValueError(str(index) + ": Invalid value for type Number.") 
    return int(num) 

# make program understand string values (or representative variable names) 
def resolve_string(index, txt): 
    if txt == None: 
        return None 

# reverse scope search 
    for scope in reversed(scopes): 
        if txt in scope: 
            return resolve_string(index, scope[txt][1]) 

    return str(txt) 

def resolve_bool(index, txt)->bool: 
    if txt == None: 
        return None 

    for scope in reversed(scopes): 
        if txt in scope: 
            return resolve_bool(index, scope[txt][1]) 

    if txt in [1, "1", True, "True"]: 
        return True 

    if txt in [0, "0", False, "False"]: 
        return False 

    if txt[0] == "!": 
        return not resolve_bool(index, txt[1:]) 

    if txt[0] == "[" and txt[-1] == "]": 
        args = txt[1:-1].split('_') 
        return compare_raw(index, *args) 

    raise ValueError(str(index) + ": Invalid value for type Bool.") 

def resolve_object(index, *args): 
    if len(args) != 1: 
        raise SyntaxError(str(index) + ": Error resolving type to primitives.") 
    if args[0][0] in ["STR", "NUM", "BOOL", "String", "Number", "Bool"]: 
        return args[0] 
    else: 
        for param in type[args[0]]: 
            return resolve_object(index, param) 

def create_number(index, *args): 
# one arg: name, no initialization | two args: name, value 
    if len(args) < 1 or len(args) > 2: 
        raise SyntaxError(str(index) + f": NUM given {len(args)} arguments (expected: 1 or 2).") 

    elif len(args) == 1: 
        args = (args[0], None) 

    if args[0] in scopes[-1]: 
        raise NameError(str(index) + ": Variable already exists.") 

    scopes[-1][args[0]] = ("Number", resolve_number(index, args[1])) 

def create_string(index, *args): 
# one arg: name, no initialization | two args: name, value 
    if len(args) < 1 or len(args) > 2: 
        raise SyntaxError(str(index) + f": STR given {len(args)} arguments (expected: 1 or 2).") 

    elif len(args) == 1: 
        args = (args[0], None) 

    if args[0] in scopes[-1]: 
        raise NameError(str(index) + ": Variable already exists.") 
    else: 
        scopes[-1][args[0]] = ("String", resolve_string(index, args[1])) 

def create_bool(index, *args): 
# one arg: name, no initialization | two args: name, value 
    if len(args) < 1 or len(args) > 2: 
        raise SyntaxError(str(index) + f": BOOL given {len(args)} arguments (expected: 1 or 2).") 

    elif len(args) == 1: 
        args = (args[0], None) 

    if args[0] in scopes[-1]: 
        raise NameError(str(index) + ": Variable already exists.") 
    else: 
        scopes[-1][args[0]] = ("Bool", resolve_bool(index, args[1])) 

def create_array(index, *args): 
    if len(args) != 3: 
        raise SyntaxError(str(index) + f": ARR given {len(args)} arguments (expected: 3).") 

    if args[0] not in ["STR", "NUM", "BOOL"]: 
        raise TypeError(str(index) + f": ARR expected (STR, NUM, BOOL) as predefined variable type.") 

    scopes[-1][args[1]] = [] 
    for _ in range(resolve_number(index, args[2])): 
        scopes[-1][args[1]].append(types[args[0]][0]) 

def string_value_of(index, x): 
    for scope in reversed(scopes): 
        if x in scope: 
            return str(scope[x][1]) 

    if x[0] == "!": 
        return str(not resolve_bool(index, x[1:])) 

    if x[0] == "[" and x[-1] == "]": 
        args = x[1:-1].split('_') 
        return str(compare_raw(index, *args)) 
    return str(x) 

def set_var_to(index, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f": SET given {len(args)} arguments (expected: 2).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            match scope[args[0]][0]: 
                case "Number": 
                    scope[args[0]] = ("Number", resolve_number(index, args[1])) 
                case "String": 
                    scope[args[0]] = ("String", resolve_string(index, args[1])) 
                case "Bool": 
                    scope[args[0]] = ("Bool", resolve_bool(index, args[1])) 
            return 

    raise NameError(str(index) + ": Referencing unknown variable.") 

def add(index, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f": ADD given {len(args)} arguments (expected: 2).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] != "Number": 
                raise TypeError(str(index) + ": Calling ADD on non-Number type.") 

            scope[args[0]] = ("Number", scope[args[0]][1] + resolve_number(index, args[1])) 
            return 
    raise NameError(str(index) + ": Referencing unknown variable.") 

def sub(index, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f": SUB given {len(args)} arguments (expected: 2).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] != "Number": 
                raise TypeError(str(index) + ": Calling SUB on non-Number type.") 

            scope[args[0]] = ("Number", scope[args[0]][1] - resolve_number(index, args[1])) 
            return 
    raise NameError(str(index) + ": Referencing unknown variable.") 

def increment(index, *args):
    if len(args) != 1: 
        raise SyntaxError(str(index) + f": INC given {len(args)} arguments (expected: 1).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] != "Number": 
                raise TypeError(str(index) + ": Calling INC on non-Number type.") 

            scope[args[0]] = ("Number", scope[args[0]][1] + 1) 
            return 
    raise NameError(str(index) + ": Referencing unknown variable.") 

def decrement(index, *args):
    if len(args) != 1: 
        raise SyntaxError(str(index) + f": DEC given {len(args)} arguments (expected: 1).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] != "Number": 
                raise TypeError(str(index) + ": Calling INC on non-Number type.") 

            scope[args[0]] = ("Number", scope[args[0]][1] - 1) 
            return 
    raise NameError(str(index) + ": Referencing unknown variable.") 

def mod(index, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f": MOD given {len(args)} arguments (expected: 2).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] != "Number": 
                raise TypeError(str(index) + ": Calling MOD on non-Number type.") 
            else: 
                scope[args[0]] = ("Number", scope[args[0]][1] % resolve_number(index, args[1])) 
                return 

    raise NameError(str(index) + ": Referencing unknown variable.") 

def flip(index, *args): 
    if len(args) != 1: 
        raise SyntaxError(str(index) + f": FLIP given {len(args)} arguments (expected: 1).") 

    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] == "Bool": 
                scope[args[0]] = (scope[args[0]][0], not scope[args[0]][1]) 
            else: 
                raise TypeError(f"{str(index)}: Calling FLIP on non-Bool type.") 
            return 
    raise NameError(str(index) + ": Referencing unknown variable.") 

def jump(index, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f": JMP given {len(args)} arguments (expected: 2).") 
    if resolve_bool(index, args[0]): 
        return resolve_number(index, args[1]) 
    return 0 

def goto(index, code, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f"GOTO given {len(args)} arguments (expected: 2).") 
    if args[1][0] != "-": 
        raise SyntaxError(str(index) + "GOTO flag must start with '-'.") 

    if resolve_bool(index, args[0]): 
        i = 0 
        while i < len(code): 
            if code[i] == args[1]: 
                return i 
            i += 1 
        raise LookupError(str(index) + ": GOTO flag not found.") 
    return index + 1 

def compare_raw(index, lhs, cmp, rhs): 
    if cmp == "IS": 
        return(string_value_of(index, lhs) == string_value_of(index, rhs)) 
    lhs = resolve_number(index, lhs) 
    rhs = resolve_number(index, rhs) 
    match cmp: 
        case "LT": 
            if lhs < rhs: return True 
        case "LEQ": 
            if lhs <= rhs: return True 
        case "EQ": 
            if lhs == rhs: return True 
        case "NEQ": 
            if lhs != rhs: return True 
        case "GEQ": 
            if lhs >= rhs: return True 
        case "GT": 
            if lhs > rhs: return True 
        case _: 
            raise ValueError(str(index) + f": Invalid comparison operator '{cmp}' (expected LT/LEQ/EQ/NEQ/GEQ/GT).") 
    return False 

def compare(index, *args): 
    if len(args) != 4: 
        raise SyntaxError(str(index) + f": CMP given {len(args)} arguments (expected: 4).") 
    scope_idx = len(scopes) - 1 
    while scope_idx >= 0: 
        if args[0] in scopes[scope_idx]: 
            if scopes[scope_idx][args[0]][0] == "Bool": 
                lhs = resolve_number(index, args[1])
                rhs = resolve_number(index, args[3]) 
                result = compare_raw(index, lhs, args[2], rhs) 
                scopes[scope_idx][args[0]] = ("Bool", result) 
            else: 
                raise TypeError(str(index) + f": Calling CMP on non Bool-type.") 
            return 
        scope_idx -= 1 
    raise NameError(str(index) + ": Referencing unknown variable.") 

def define(index, code, *args): 
    if args[0] in functions: 
        raise NameError(str(index) + ": Function name already exists.") 

    if len(args) % 2 == 0: 
        raise SyntaxError(str(index) + f": DEF given {len(args)} arguments (expected: 1, 3, 5, ...).") 

    functions[args[0]] = [int((len(args)-1) / 2), ["SCOPE ADD"]] 
    i = 1 
    while i < len(args): 
        if args[i] not in ["STR", "NUM", "BOOL"]: 
            raise SyntaxError(str(index) + ": DEF expected (STR, NUM, BOOL) as predefined variable type.") 
        functions[args[0]][1].append(args[i] + " " + args[i + 1]) 
        i += 2 

    i = index + 1 
    while i < len(code) and code[i] != "ENDDEF": 
        functions[args[0]][1].append(code[i]) 
        i += 1 
    if i >= len(code): 
        raise SyntaxError(str(index) + ": DEF expected ENDDEF") 

    functions[args[0]][1].append("SCOPE DEL") 

    return i - index 

def handle_scope(index, *args): 
    if len(args) != 1: 
        raise SyntaxError(str(index) + f": SCOPE given {len(args)} arguments (expected: 1).") 
    match args[0]: 
        case "ADD": 
            scopes.append({}) 
        case "DEL": 
            del scopes[-1] 
        case _: 
            raise SyntaxError(str(index) + ": SCOPE expected (ADD, DEL) as argument.") 

def handle_return(index, *args): 
    if len(args) != 2: 
        raise SyntaxError(str(index) + f": RET given {len(args)} arguments (expected: 2).") 
    match args[0]: 
        case "STR": 
            return_value = ("String", resolve_string(index, args[1])) 
        case "NUM": 
            return_value = ("Number", resolve_number(index, args[1])) 
        case "BOOL": 
            return_value = ("Bool", resolve_bool(index, args[1])) 
    try: 
        scopes[-2]["@RET"] = return_value 
    except: 
        raise LookupError(str(index) + ": RET used in global scope.") 

def create_type(index, *args): 
    if len(args) < 3 or len(args)%2 == 0: 
        raise SyntaxError(str(index) + f": TYPE given {len(args)} arguments (expected: 3, 5, 7, ...).") 
    type_name = args[0] 
    params = [resolve_object(index, (args[2*x+1], args[2*x+2])) for x in range(int((len(args)-1)/2))] 
    print(params) 
    types[type_name] = params 
    return 

def create_instanceOf_type(index, call, *args): 
    return 

def get_input(index, *args): 
    if len(args) != 1: 
        raise SyntaxError(str(index) + f": IN given {len(args)} arguments (expected: 1).") 
    for scope in reversed(scopes): 
        if args[0] in scope: 
            if scope[args[0]][0] != "String": 
                raise TypeError(str(index) + ": Calling IN on non String-type.") 
            else: 
                scope[args[0]] = ("String", input(args[0] + ": ")) 
                return 

    raise NameError(str(index) + ": Referencing unknown variable.") 

def set_output(index, *args): 
    output = [] 
    if len(args) == 0: 
        print() 
        return
    for arg in args: 
        output.append(string_value_of(index, arg)) 

    print(" ".join(output)) 

def import_module(index, *args):
    for arg in args:
        try:
            with open(f"{arg}.cobmod") as f:
                code = f.read().splitlines()
            run(code)
        except:
            raise ImportError(str(index) + f": Unknown module '{args[0]}'")

def execute(index, program): 
    line_split = asplit(index, program[index]) 

    call = line_split[0] 
    args = line_split[1:]

    match call: 
        case "NUM": 
            create_number(index, *args) 

        case "STR": 
            create_string(index, *args) 

        case "BOOL": 
            create_bool(index, *args) 

        case "ARR": 
            create_array(index, *args) 

        case "SET": 
            set_var_to(index, *args) 

        case "ADD": 
            add(index, *args)

        case "SUB":
            sub(index, *args)
        
        case "INC":
            increment(index, *args)
        
        case "DEC":
            decrement(index, *args)

        case "MOD": 
            mod(index, *args) 

        case "FLIP": 
            flip(index, *args) 

        case "CMP": 
            compare(index, *args) 

        case "IN": 
            get_input(index, *args) 

        case "OUT": 
            set_output(index, *args) 

        case "JMP": 
            return index + 1 + jump(index, *args) 

        case "GOTO": 
            return goto(index, program, *args) 

        case "DEF": 
            return index + define(index, program, *args) 

        case "SCOPE": 
            handle_scope(index, *args) 

        case "RET": 
            handle_return(index, *args) 
            return len(program) - 1
        
        case "CLS":
            cls(100)

        case "TYPE": 
            create_type(index, *args)

        case "IMPORT":
            import_module(index, *args)

        case "//" | "" | "ENDDEF": 
            pass 

        case _: 
            if call in functions: 
                if len(args) == functions[call][0]: 
                    inserted_values = functions[call][1].copy() 
                    i = 0 
                    while i < len(args): 
                        inserted_values[i+1] += " " + str(args[i]) 
                        i += 1 
                    run(inserted_values) 
                else: 
                    raise SyntaxError(str(index) + f": {call} given {len(args)} arguments (expected {functions[call][0]}).") 
            elif call in types: 
                create_instanceOf_type(index, call, *args) 
            elif call[0] == "-": 
                pass 
            else: 
                raise SyntaxError(str(index) + ": Unknown command.") 
    return index + 1 

def run(program): 
    index = 0 

    while index < len(program):
        index = execute(index, program) 

with open("code.cobraasm") as f:
    code = f.read().splitlines() 

cls(100) 
run(code)