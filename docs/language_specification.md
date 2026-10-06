# AutoScript Language Specification

File Extension: `.as`

AutoScript is a domain-specific automation language supporting browser navigation, delay control, keyboard key presses, string typing, loops, comments, and variable assignments.

## 1. Keywords & Commands

| Keyword | Description | Syntax Example |
|---|---|---|
| `OPEN` | Opens a URL in the browser | `OPEN "https://example.com"` |
| `GAP` | Delays execution for N seconds | `GAP 5` |
| `TYPE` | Types text into active input | `TYPE "Student"` |
| `PRESS` | Presses a key (with optional repeat count) | `PRESS TAB 9` |
| `LOOP` | Repeats enclosed statements N times | `LOOP 3 { PRESS TAB }` |
| `SET` | Declares/assigns a variable symbol | `SET WAIT_TIME = 5` |

## 2. Supported Keys
`TAB`, `ENTER`, `ESC`, `SPACE`, `BACKSPACE`, `UP`, `DOWN`, `LEFT`, `RIGHT`, `SHIFT`, `CTRL`, `ALT`.

## 3. Comments
- Single-line hash comments: `# Comment`
- Single-line slash comments: `// Comment`

## 4. Semantic Rules
1. `GAP` duration must be a positive number (`> 0`).
2. `LOOP` count must be a positive integer (`> 0`).
3. `PRESS` key count must be a positive integer (`>= 1`).
4. Variable references must be declared prior to use (`SET`).
