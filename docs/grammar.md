# AutoScript Formal Grammar (BNF / EBNF)

```ebnf
Program         ::= StatementList EOF ;

StatementList   ::= { Statement } ;

Statement       ::= OpenStmt
                  | GapStmt
                  | TypeStmt
                  | PressStmt
                  | LoopStmt
                  | SetStmt ;

OpenStmt        ::= "OPEN" Expression ;

GapStmt         ::= "GAP" Expression ;

TypeStmt        ::= "TYPE" Expression ;

PressStmt       ::= "PRESS" KeyName [ Expression ] ;

LoopStmt        ::= "LOOP" Expression "{" StatementList "}" ;

SetStmt         ::= "SET" Identifier "=" Expression ;

Expression      ::= StringLiteral
                  | NumberLiteral
                  | Identifier ;

KeyName         ::= "TAB" | "ENTER" | "ESC" | "SPACE" | "BACKSPACE"
                  | "UP" | "DOWN" | "LEFT" | "RIGHT" | "SHIFT" | "CTRL" | "ALT" ;

StringLiteral   ::= '"' { Character } '"' ;
NumberLiteral   ::= [ "-" ] Digit { Digit } ;
Identifier      ::= Letter { Letter | Digit | "_" } ;
```
