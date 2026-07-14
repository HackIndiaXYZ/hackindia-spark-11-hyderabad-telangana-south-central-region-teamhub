import sys
import traceback
from io import StringIO
from typing import Any


def _serialize(val: Any) -> Any:
    if isinstance(val, (int, float, bool, str, type(None))):
        return val
    if isinstance(val, (list, tuple)):
        return [_serialize(v) for v in val]
    if isinstance(val, dict):
        return {str(k): _serialize(v) for k, v in val.items()}
    if isinstance(val, set):
        return [v for v in val]
    return str(val)


class TraceRecorder:
    def __init__(self):
        self.steps: list[dict] = []
        self.step_counter = 0
        self.variables: dict[str, Any] = {}
        self.output_lines: list[str] = []
        self._current_line = 0
        self._printed_lines: set[int] = set()
        self._skip_next = False

    def _snap_vars(self) -> dict[str, Any]:
        return {k: _serialize(v) for k, v in self.variables.items() if not k.startswith('_')}

    def record(self, line: int, operation: str, changed: list[str] | None = None,
               output: str = "", explanation: str = ""):
        self.step_counter += 1
        self.steps.append({
            "step": self.step_counter,
            "line": line,
            "operation": operation,
            "variables": self._snap_vars(),
            "dataStructure": None,
            "highlightedIndexes": [],
            "callStack": [],
            "output": output,
            "explanation": explanation,
            "changedVariables": changed or [],
            "loopIteration": None,
            "conditionResult": None,
        })

    def mark_error(self, line: int, msg: str):
        self.record(line, "error", output=msg, explanation=f"Error: {msg}")

    def mark_condition(self, line: int, result: bool):
        self.record(line, "condition", changed=[],
                    output="True" if result else "False",
                    explanation=f"Condition evaluated to {result}")


    def mark_loop(self, line: int, iteration: int):
        self.record(line, "loop_iteration", changed=[],
                    output=f"Iteration {iteration}",
                    explanation=f"Loop iteration {iteration}")


def run_and_trace(code: str, input_data: str = "") -> dict:
    recorder = TraceRecorder()

    old_stdout = sys.stdout
    old_stdin = sys.stdin
    sys.stdout = StringIO()
    if input_data:
        sys.stdin = StringIO(input_data)

    exit_status = 0
    runtime_error = ""
    compile_error = ""
    captured_output = ""

    lines = code.split('\n')
    _trace_depth = 0
    MAX_STEPS = 500

    def trace_callback(frame, event, arg):
        nonlocal _trace_depth
        if _trace_depth > 10 or recorder.step_counter >= MAX_STEPS:
            return None
        _trace_depth += 1
        try:
            if event == 'line':
                line_no = frame.f_lineno
                if line_no <= len(lines) and line_no > 0:
                    for k, v in frame.f_locals.items():
                        if not k.startswith('_'):
                            recorder.variables[k] = v
                    recorder.record(line_no, 'execution', changed=list(frame.f_locals.keys()))
            elif event == 'call':
                func_name = frame.f_code.co_name
                if func_name != '<module>':
                    recorder.record(frame.f_lineno, 'function_call', changed=[],
                                    output=f"-> {func_name}()", explanation=f"Calling {func_name}")
            elif event == 'return':
                func_name = frame.f_code.co_name
                if func_name != '<module>':
                    recorder.record(frame.f_lineno, 'function_return', changed=[],
                                    output=f"<- {func_name}", explanation=f"Returning from {func_name}")
            return trace_callback
        finally:
            _trace_depth -= 1

    try:
        compile(code, '<user_code>', 'exec')
    except SyntaxError as e:
        recorder.mark_error(1, f"Syntax error: {e.msg}")
        return {
            "steps": recorder.steps, "total_steps": 0,
            "algorithm_type": "syntax_error",
            "time_complexity": "N/A", "space_complexity": "N/A",
            "output_lines": [], "errors": [str(e)],
            "runtime_error": "", "compile_error": str(e),
            "exit_status": 1, "execution_time_ms": 0, "memory_usage_kb": 0,
            "data_values": [],
        }

    recorder.record(1, "start", explanation="Code execution started")
    g = {"_tracer": recorder, "__builtins__": __builtins__}

    try:
        sys.settrace(trace_callback)
        exec(code, g)
    except SystemExit as e:
        exit_status = e.code if e.code else 0
    except Exception as e:
        runtime_error = f"{type(e).__name__}: {str(e)}"
        recorder.mark_error(1, runtime_error)
        exit_status = 1
    finally:
        sys.settrace(None)
        captured_output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        sys.stdin = old_stdin

    final_vars = {k: _serialize(v) for k, v in g.items()
                  if not k.startswith("_") and k != "__builtins__"}

    recorder.record(1, "complete", changed=list(final_vars.keys()),
                    output=captured_output.strip(), explanation="Code execution complete")

    return {
        "steps": recorder.steps,
        "total_steps": len(recorder.steps),
        "algorithm_type": "general",
        "time_complexity": "",
        "space_complexity": "",
        "output_lines": [captured_output] if captured_output else [],
        "errors": [runtime_error] if runtime_error else [],
        "runtime_error": runtime_error,
        "compile_error": compile_error,
        "exit_status": exit_status,
        "execution_time_ms": 0,
        "memory_usage_kb": 0,
        "data_values": [],
    }
