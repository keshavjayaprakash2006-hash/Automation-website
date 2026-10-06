"""
AutoScript Compiler - Python Code Generator
Translates Intermediate Representation (IR) instructions into clean, executable Python code.
"""

from typing import List
from backend.ir.ir_generator import IRInstruction

class PythonCodeGenerator:
    def __init__(self, ir_instructions: List[IRInstruction]):
        self.ir_instructions = ir_instructions
        self.indent_level = 0
        self.indent_str = "    "

    def indent(self) -> str:
        return self.indent_str * self.indent_level

    def generate(self) -> str:
        lines: List[str] = [
            "# AutoScript Generated Python Code",
            "# Target Automation Libraries: webbrowser, time, pyautogui",
            "import webbrowser",
            "import time",
            "import pyautogui",
            "",
            "pyautogui.FAILSAFE = True",
            ""
        ]

        for instr in self.ir_instructions:
            op = instr.op
            args = instr.args

            if op == "OPEN_URL":
                url = args[0]
                lines.append(f"{self.indent()}webbrowser.open({repr(url)})")

            elif op == "WAIT":
                duration = args[0]
                lines.append(f"{self.indent()}time.sleep({duration})")

            elif op == "TYPE_TEXT":
                text = args[0]
                lines.append(f"{self.indent()}pyautogui.write({repr(text)})")

            elif op == "PRESS_KEY":
                key = str(args[0]).lower()
                count = args[1] if len(args) > 1 else 1
                if count == 1:
                    lines.append(f"{self.indent()}pyautogui.press({repr(key)})")
                else:
                    lines.append(f"{self.indent()}pyautogui.press({repr(key)}, presses={count})")

            elif op == "SET_VAR":
                var_name = args[0]
                val = args[1]
                val_repr = repr(val) if isinstance(val, str) else str(val)
                lines.append(f"{self.indent()}{var_name} = {val_repr}")

            elif op == "LOOP_START":
                loop_count = args[0]
                lines.append(f"{self.indent()}for _ in range({loop_count}):")
                self.indent_level += 1

            elif op == "LOOP_END":
                self.indent_level = max(0, self.indent_level - 1)

        return "\n".join(lines)
