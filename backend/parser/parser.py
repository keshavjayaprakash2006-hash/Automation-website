"""
AutoScript Compiler - Recursive-Descent Parser
Parses a token stream into an Abstract Syntax Tree (AST) and Concrete Parse Tree (CST).
"""

from typing import List, Dict, Any, Tuple
from backend.lexer.token import Token, TokenType
from backend.ast.nodes import (
    ProgramNode, OpenNode, GapNode, TypeNode, PressNode,
    LoopNode, SetNode, LiteralNode, VariableNode, ASTNode
)
from backend.errors.compiler_errors import CompilerError

class Parser:
    def __init__(self, tokens: List[Token], source_code: str = ""):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        self.source_code = source_code
        self.pos = 0

    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", 1, 1)

    def peek_token(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, "", 1, 1)

    def error(self, message: str, token: Token = None):
        t = token or self.current_token()
        raise CompilerError("SYNTAX", message, t.line, t.column, self.source_code)

    def consume(self, expected_type: TokenType = None, expected_value: str = None) -> Token:
        token = self.current_token()
        if expected_type and token.type != expected_type:
            self.error(f"Expected token type '{expected_type.value}' but found '{token.type.value}' ({repr(token.value)})", token)
        if expected_value and str(token.value).upper() != expected_value.upper():
            self.error(f"Expected '{expected_value}' but found '{token.value}'", token)
        self.pos += 1
        return token

    def parse(self) -> Tuple[ProgramNode, Dict[str, Any]]:
        """
        Parses the tokens into an AST and Concrete Parse Tree (CST).
        Returns tuple of (ast_root, parse_tree_dict).
        """
        statements: List[ASTNode] = []
        cst_children: List[Dict[str, Any]] = []

        while self.current_token().type != TokenType.EOF:
            stmt_ast, stmt_cst = self.parse_statement()
            statements.append(stmt_ast)
            cst_children.append(stmt_cst)

        ast_root = ProgramNode(statements, line=1, column=1)
        cst_root = {
            "name": "PROGRAM",
            "children": cst_children if cst_children else [{"name": "<empty>"}]
        }
        return ast_root, cst_root

    def parse_statement(self) -> Tuple[ASTNode, Dict[str, Any]]:
        token = self.current_token()

        if token.type == TokenType.COMMAND:
            cmd = str(token.value).upper()
            if cmd == "OPEN":
                return self.parse_open_statement()
            elif cmd == "GAP":
                return self.parse_gap_statement()
            elif cmd == "TYPE":
                return self.parse_type_statement()
            elif cmd == "PRESS":
                return self.parse_press_statement()
            elif cmd == "LOOP":
                return self.parse_loop_statement()
            elif cmd == "SET":
                return self.parse_set_statement()
            else:
                self.error(f"Unknown command statement '{cmd}'", token)

        self.error(f"Unexpected token '{token.value}' at start of statement", token)

    def parse_expression(self) -> Tuple[ASTNode, Dict[str, Any]]:
        token = self.current_token()
        if token.type == TokenType.STRING:
            t = self.consume(TokenType.STRING)
            ast = LiteralNode(t.value, "STRING", t.line, t.column)
            cst = {"name": f"STRING: {repr(t.value)}"}
            return ast, cst
        elif token.type == TokenType.NUMBER:
            t = self.consume(TokenType.NUMBER)
            ast = LiteralNode(t.value, "NUMBER", t.line, t.column)
            cst = {"name": f"NUMBER: {t.value}"}
            return ast, cst
        elif token.type == TokenType.IDENTIFIER:
            t = self.consume(TokenType.IDENTIFIER)
            ast = VariableNode(t.value, t.line, t.column)
            cst = {"name": f"IDENTIFIER: {t.value}"}
            return ast, cst
        else:
            self.error(f"Expected expression (STRING, NUMBER, or IDENTIFIER) but found '{token.value}'", token)

    def parse_open_statement(self) -> Tuple[OpenNode, Dict[str, Any]]:
        open_tok = self.consume(TokenType.COMMAND, "OPEN")
        url_ast, url_cst = self.parse_expression()

        # Open expects a string or variable identifier
        if isinstance(url_ast, LiteralNode) and url_ast.literal_type != "STRING":
            self.error("OPEN command expects a string URL", self.tokens[self.pos-1])

        ast = OpenNode(url_ast, open_tok.line, open_tok.column)
        cst = {
            "name": "OPEN_STMT",
            "children": [
                {"name": "COMMAND: OPEN"},
                url_cst
            ]
        }
        return ast, cst

    def parse_gap_statement(self) -> Tuple[GapNode, Dict[str, Any]]:
        gap_tok = self.consume(TokenType.COMMAND, "GAP")
        dur_ast, dur_cst = self.parse_expression()

        if isinstance(dur_ast, LiteralNode) and dur_ast.literal_type != "NUMBER":
            self.error("GAP command expects a numeric duration", self.tokens[self.pos-1])

        ast = GapNode(dur_ast, gap_tok.line, gap_tok.column)
        cst = {
            "name": "GAP_STMT",
            "children": [
                {"name": "COMMAND: GAP"},
                dur_cst
            ]
        }
        return ast, cst

    def parse_type_statement(self) -> Tuple[TypeNode, Dict[str, Any]]:
        type_tok = self.consume(TokenType.COMMAND, "TYPE")
        text_ast, text_cst = self.parse_expression()

        if isinstance(text_ast, LiteralNode) and text_ast.literal_type != "STRING":
            self.error("TYPE command expects a string text argument", self.tokens[self.pos-1])

        ast = TypeNode(text_ast, type_tok.line, type_tok.column)
        cst = {
            "name": "TYPE_STMT",
            "children": [
                {"name": "COMMAND: TYPE"},
                text_cst
            ]
        }
        return ast, cst

    def parse_press_statement(self) -> Tuple[PressNode, Dict[str, Any]]:
        press_tok = self.consume(TokenType.COMMAND, "PRESS")
        curr = self.current_token()

        if curr.type not in (TokenType.KEY, TokenType.IDENTIFIER):
            self.error(f"Expected KEY after PRESS but found '{curr.value}'", curr)

        key_tok = self.consume()
        key_val = str(key_tok.value)

        # Optional count
        count_ast: ASTNode = LiteralNode(1, "NUMBER", key_tok.line, key_tok.column)
        count_cst = {"name": "NUMBER (default): 1"}

        next_tok = self.current_token()
        if next_tok.type in (TokenType.NUMBER, TokenType.IDENTIFIER):
            count_ast, count_cst = self.parse_expression()
            if isinstance(count_ast, LiteralNode) and count_ast.literal_type != "NUMBER":
                self.error("PRESS repeat count must be a number", next_tok)

        ast = PressNode(key_val, count_ast, press_tok.line, press_tok.column)
        cst = {
            "name": "PRESS_STMT",
            "children": [
                {"name": "COMMAND: PRESS"},
                {"name": f"KEY: {key_val}"},
                count_cst
            ]
        }
        return ast, cst

    def parse_loop_statement(self) -> Tuple[LoopNode, Dict[str, Any]]:
        loop_tok = self.consume(TokenType.COMMAND, "LOOP")
        count_ast, count_cst = self.parse_expression()

        if isinstance(count_ast, LiteralNode) and count_ast.literal_type != "NUMBER":
            self.error("LOOP count must be a number", self.tokens[self.pos-1])

        lbrace = self.consume(TokenType.LBRACE)

        body_ast: List[ASTNode] = []
        body_cst: List[Dict[str, Any]] = []

        while self.current_token().type != TokenType.RBRACE:
            if self.current_token().type == TokenType.EOF:
                self.error("Unmatched '{': Expected '}' to close LOOP block", lbrace)
            stmt_ast, stmt_cst = self.parse_statement()
            body_ast.append(stmt_ast)
            body_cst.append(stmt_cst)

        self.consume(TokenType.RBRACE)

        ast = LoopNode(count_ast, body_ast, loop_tok.line, loop_tok.column)
        cst = {
            "name": "LOOP_STMT",
            "children": [
                {"name": "COMMAND: LOOP"},
                count_cst,
                {
                    "name": "BLOCK",
                    "children": body_cst if body_cst else [{"name": "<empty_block>"}]
                }
            ]
        }
        return ast, cst

    def parse_set_statement(self) -> Tuple[SetNode, Dict[str, Any]]:
        set_tok = self.consume(TokenType.COMMAND, "SET")
        var_tok = self.consume(TokenType.IDENTIFIER)
        var_name = str(var_tok.value)
        self.consume(TokenType.EQUALS)

        val_ast, val_cst = self.parse_expression()

        ast = SetNode(var_name, val_ast, set_tok.line, set_tok.column)
        cst = {
            "name": "SET_STMT",
            "children": [
                {"name": "COMMAND: SET"},
                {"name": f"IDENTIFIER: {var_name}"},
                {"name": "EQUALS: ="},
                val_cst
            ]
        }
        return ast, cst
