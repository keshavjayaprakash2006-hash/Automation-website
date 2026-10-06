from tokeniser import tokenize_file

def execute(tokens):
    i = 0
    length = len(tokens)

    while i < length:
        kind, value = tokens[i]

        if kind == 'NEWLINE':
            i += 1
            continue

        if kind == 'COMMAND':
            if value == 'OPEN':
                url = tokens[i+1][1]
                print(f"webbrowser.open('{url}')")
                i += 2

            elif value == 'GAP':
                duration = int(tokens[i+1][1])
                print(f"time.sleep({duration})")
                i += 2

            elif value == 'TYPE':
                text = tokens[i+1][1]
                print(f"pyautogui.write('{text}')")
                i += 2

            elif value == 'PRESS':
                key = tokens[i+1][1].lower()
                count = 1
                i += 2
                if i < length and tokens[i][0] == 'NUMBER':
                    count = int(tokens[i][1])
                    i += 1
                print(f"pyautogui.press('{key}', presses={count})")

        else:
            i += 1

my_tokens = tokenize_file('sample_file.txt')
execute(my_tokens)