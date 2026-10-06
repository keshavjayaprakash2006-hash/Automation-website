"""
AutoScript Compiler - Lexical Analyzer (Lexer)
Converts raw AutoScript source code into a sequence of structured Tokens.
"""

from typing import List
from backend.lexer.token import Token, TokenType
from backend.errors.compiler_errors import CompilerError

COMMANDS = {"OPEN", "GAP", "PRESS", "TYPE", "LOOP", "SET"}
KEYS = {
    "TAB", "ENTER", "ESC", "SPACE", "BACKSPACE",
    "UP", "DOWN", "LEFT", "RIGHT", "SHIFT", "CTRL", "ALT"
}

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.i = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, message: str, line: int = None, column: int = None):
        l = line if line is not None else self.line
        c = column if column is not None else self.column
        raise CompilerError("LEXICAL", message, l, c, self.source)

    def tokenize(self) -> List[Token]:
        self.tokens = []
        self.i = 0
        self.line = 1
        self.column = 1

        while self.i < self.length:
            char = self.source[self.i]

            # Whitespace handling (space, tab, carriage return)
            if char in ' \t\r':
                if char == '\t':
                    self.column += 4
                else:
                    self.column += 1
                self.i += 1
                continue

            # Newline handling
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.line += 1
                self.column = 1
                self.i += 1
                continue

            # Comments: '#' or '//'
            if char == '#' or (char == '/' and self.i + 1 < self.length and self.source[self.i + 1] == '/'):
                while self.i < self.length and self.source[self.i] != '\n':
                    self.i += 1
                    self.column += 1
                continue

            # Equals sign '='
            if char == '=':
                self.tokens.append(Token(TokenType.EQUALS, '=', self.line, self.column))
                self.i += 1
                self.column += 1
                continue

            # Left Brace '{'
            if char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, self.column))
                self.i += 1
                self.column += 1
                continue

            # Right Brace '}'
            if char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, self.column))
                self.i += 1
                self.column += 1
                continue

            # Strings: "..."
            if char == '"':
                start_line = self.line
                start_col = self.column
                self.i += 1
                self.column += 1
                string_chars = []
                closed = False

                while self.i < self.length:
                    curr = self.source[self.i]
                    if curr == '"':
                        closed = True
                        self.i += 1
                        self.column += 1
                        break
                    elif curr == '\n':
                        self.error("Unterminated string literal (newline encountered)", start_line, start_col)
                    else:
                        string_chars.append(curr)
                        self.i += 1
                        self.column += 1

                if not closed:
                    self.error("Unterminated string literal", start_line, start_col)

                val = "".join(string_chars)
                self.tokens.append(Token(TokenType.STRING, val, start_line, start_col))
                continue

            # Numbers: positive integers (or negative numbers if preceded by '-')
            if char.isdigit() or (char == '-' and self.i + 1 < self.length and self.source[self.i + 1].isdigit()):
                start_line = self.line
                start_col = self.column
                num_chars = [char]
                self.i += 1
                self.column += 1

                while self.i < self.length and self.source[self.i].isdigit():
                    num_chars.append(self.source[self.i])
                    self.i += 1
                    self.column += 1

                raw_val = "".join(num_chars)
                try:
                    val = int(raw_val)
                    self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col))
                except ValueError:
                    self.error(f"Invalid numeric literal '{raw_val}'", start_line, start_col)
                continue

            # Identifiers / Commands / Keys
            if char.isalpha() or char == '_':
                start_line = self.line
                start_col = self.column
                word_chars = []

                while self.i < self.length and (self.source[self.i].isalnum() or self.source[self.i] == '_'):
                    word_chars.append(self.source[self.i])
                    self.i += 1
                    self.column += 1

                word = "".join(word_chars)
                upper_word = word.upper()

                if upper_word in COMMANDS:
                    self.tokens.append(Token(TokenType.COMMAND, upper_word, start_line, start_col))
                elif upper_word in KEYS:
                    self.tokens.append(Token(TokenType.KEY, upper_word, start_line, start_col))
                else:
                    # Treat as variable / identifier
                    self.tokens.append(Token(TokenType.IDENTIFIER, word, start_line, start_col))
                continue

            # Invalid / unexpected character
            self.error(f"Unexpected character '{char}'", self.line, self.column)

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
