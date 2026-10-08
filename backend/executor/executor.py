"""
AutoScript Compiler - Execution Engine
Supports Mode 1 (Simulation trace) and Mode 2 (Real PyAutoGUI execution operating directly on validated IR instructions).
"""

import time
import datetime
import threading
import sys
import io
from typing import List, Dict, Any
from backend.ir.ir_generator import IRInstruction

class Executor:
    _active_thread: threading.Thread = None
    _stop_flag: bool = False

    @classmethod
    def simulate(cls, ir_instructions: List[IRInstruction]) -> List[str]:
        """Runs Mode 1: Safe simulation and returns timestamped execution trace logs."""
        trace: List[str] = ["=== AUTOSCRIPT SIMULATION MODE STARTED ==="]
        step_num = 1
        curr_time = datetime.datetime.now()

        def log(msg: str):
            nonlocal curr_time, step_num
            timestamp = curr_time.strftime("%H:%M:%S")
            trace.append(f"[{timestamp}] [Step {step_num}] {msg}")
            step_num += 1

        cls._simulate_instructions(ir_instructions, log, curr_time_ref=[curr_time])
        trace.append("=== SIMULATION COMPLETED SUCCESSFULLY ===")
        return trace

    @classmethod
    def _simulate_instructions(cls, instructions: List[IRInstruction], log_func, curr_time_ref, loop_context: str = ""):
        i = 0
        n = len(instructions)
        while i < n:
            instr = instructions[i]
            op = instr.op
            args = instr.args

            if op == "OPEN_URL":
                log_func(f"OPEN URL -> '{args[0]}'")
                curr_time_ref[0] += datetime.timedelta(seconds=1)

            elif op == "WAIT":
                dur = args[0]
                log_func(f"WAIT -> {dur} seconds")
                curr_time_ref[0] += datetime.timedelta(seconds=dur)

            elif op == "TYPE_TEXT":
                log_func(f"TYPE -> '{args[0]}'")
                curr_time_ref[0] += datetime.timedelta(seconds=1)

            elif op == "PRESS_KEY":
                key = str(args[0]).upper()
                cnt = args[1] if len(args) > 1 else 1
                log_func(f"PRESS KEY -> {key} (repeat={cnt})")
                curr_time_ref[0] += datetime.timedelta(seconds=1)

            elif op == "SET_VAR":
                log_func(f"SET VARIABLE -> {args[0]} = {repr(args[1])}")

            elif op == "LOOP_START":
                loop_count = int(args[0])
                # Find matching LOOP_END
                body_instructions = []
                depth = 1
                j = i + 1
                while j < n:
                    if instructions[j].op == "LOOP_START":
                        depth += 1
                    elif instructions[j].op == "LOOP_END":
                        depth -= 1
                        if depth == 0:
                            break
                    body_instructions.append(instructions[j])
                    j += 1

                for iter_num in range(1, loop_count + 1):
                    log_func(f"LOOP START (Iteration {iter_num}/{loop_count})")
                    cls._simulate_instructions(body_instructions, log_func, curr_time_ref, loop_context=f"Iteration {iter_num}")
                    log_func(f"LOOP END (Iteration {iter_num}/{loop_count})")

                i = j  # Skip past LOOP_END

            i += 1

    @classmethod
    def run_real_ir(cls, ir_instructions: List[IRInstruction]) -> Dict[str, Any]:
        """
        Runs Mode 2: Real PyAutoGUI automation execution safely directly from validated IR instructions.
        Avoids direct string exec() of arbitrary user code.
        """
        if cls._active_thread and cls._active_thread.is_alive():
            return {
                "success": False,
                "message": "An automation script is already running!",
                "logs": []
            }

        cls._stop_flag = False
        logs: List[str] = ["=== REAL AUTOMATION EXECUTION STARTED (FROM VALIDATED IR) ==="]

        def target():
            try:
                cls._execute_ir_list(ir_instructions, logs)
                logs.append("=== REAL AUTOMATION COMPLETED CLEANLY ===")
            except Exception as e:
                logs.append(f"Real execution error: {str(e)}")

        thread = threading.Thread(target=target, daemon=True)
        cls._active_thread = thread
        thread.start()
        thread.join(timeout=30)  # max 30s timeout

        return {
            "success": True,
            "message": "Automation execution completed.",
            "logs": logs
        }

    @classmethod
    def _execute_ir_list(cls, instructions: List[IRInstruction], logs: List[str]):
        import webbrowser
        import pyautogui
        pyautogui.FAILSAFE = True

        i = 0
        n = len(instructions)
        while i < n:
            if cls._stop_flag:
                logs.append("[EMERGENCY STOP] Execution halted by user request.")
                break

            instr = instructions[i]
            op = instr.op
            args = instr.args

            if op == "OPEN_URL":
                url = str(args[0])
                logs.append(f"Executing: OPEN URL '{url}'")
                webbrowser.open(url)

            elif op == "WAIT":
                dur = float(args[0])
                logs.append(f"Executing: WAIT {dur}s")
                time.sleep(dur)

            elif op == "TYPE_TEXT":
                txt = str(args[0])
                logs.append(f"Executing: TYPE '{txt}'")
                pyautogui.write(txt, interval=0.05)

            elif op == "PRESS_KEY":
                key = str(args[0]).lower()
                cnt = int(args[1]) if len(args) > 1 else 1
                logs.append(f"Executing: PRESS KEY {key.upper()} (x{cnt})")
                pyautogui.press(key, presses=cnt, interval=0.05)

            elif op == "LOOP_START":
                loop_count = int(args[0])
                body_instructions = []
                depth = 1
                j = i + 1
                while j < n:
                    if instructions[j].op == "LOOP_START":
                        depth += 1
                    elif instructions[j].op == "LOOP_END":
                        depth -= 1
                        if depth == 0:
                            break
                    body_instructions.append(instructions[j])
                    j += 1

                for iter_num in range(1, loop_count + 1):
                    if cls._stop_flag:
                        break
                    logs.append(f"Loop Iteration {iter_num}/{loop_count}")
                    cls._execute_ir_list(body_instructions, logs)

                i = j  # Skip to LOOP_END

            i += 1

    @classmethod
    def stop(cls) -> Dict[str, Any]:
        cls._stop_flag = True
        return {"success": True, "message": "Emergency stop signal sent."}
