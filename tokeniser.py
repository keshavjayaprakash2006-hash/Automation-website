def tokenize_file(filepath):
    try:
        with open(filepath, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'")
        return []

    tokens = []
    i = 0
    length = len(code)

    while i < length:
        char = code[i]

        if char in ' \t\r':
            i += 1
            continue

        if char == '\n':
            tokens.append(['NEWLINE', '\n'])
            i += 1
            continue

        if char == '#' or code[i:i+2] == '//':
            while i < length and code[i] != '\n':
                i += 1
            continue

        if char == '"':
            i += 1
            start = i
            while i < length and code[i] != '"':
                i += 1
            tokens.append(['STRING', code[start:i]])
            i += 1
            continue

        if char.isdigit():
            start = i
            while i < length and code[i].isdigit():
                i += 1
            tokens.append(['NUMBER', code[start:i]])
            continue

        if char == '{':
            tokens.append(['LBRACE', '{'])
            i += 1
            continue

        if char == '}':
            tokens.append(['RBRACE', '}'])
            i += 1
            continue

        if char.isalpha():
            start = i
            while i < length and (code[i].isalnum() or code[i] == '_'):
                i += 1
            word = code[start:i]
            
            if word in ["OPEN", "GAP", "PRESS", "TYPE", "LOOP"]:
                tokens.append(['COMMAND', word])
            elif word in ["TAB", "ENTER"]:
                tokens.append(['KEY', word])
            else:
                raise RuntimeError(f"Unknown keyword: {word}")
            continue

        raise RuntimeError(f"Unexpected character: {char}")

    return tokens


tokenized_output = tokenize_file('sample_file.txt')
    
for token in tokenized_output:
    print(token)