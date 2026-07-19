EXECUTION_TRACE_VERSION = "1.0"


def normalize_trace(raw_trace: dict) -> dict:
    steps = raw_trace.get("steps", [])
    output_lines = raw_trace.get("output_lines", [])
    errors = raw_trace.get("errors", [])
    exec_time = raw_trace.get("execution_time_ms", 0)
    memory_usage = raw_trace.get("memory_usage_kb", 0)

    normalized_steps = []
    for s in steps:
        normalized_steps.append({
            "step": s.get("step", 0),
            "line": s.get("line", 1),
            "operation": s.get("operation", ""),
            "variables": s.get("variables", {}),
            "dataStructure": s.get("dataStructure"),
            "highlightedIndexes": s.get("highlightedIndexes", []),
            "callStack": s.get("callStack", []),
            "output": s.get("output", ""),
            "explanation": s.get("explanation", ""),
            "complexity": s.get("complexity"),
            "changedVariables": s.get("changedVariables", []),
            "loopIteration": s.get("loopIteration"),
            "conditionResult": s.get("conditionResult"),
        })

    return {
        "version": EXECUTION_TRACE_VERSION,
        "steps": normalized_steps,
        "total_steps": len(normalized_steps),
        "algorithm_type": raw_trace.get("algorithm_type", "general"),
        "time_complexity": raw_trace.get("time_complexity", ""),
        "space_complexity": raw_trace.get("space_complexity", ""),
        "program_output": {
            "stdout": "".join(output_lines),
            "stderr": "".join(errors),
            "compile_error": raw_trace.get("compile_error", ""),
            "runtime_error": raw_trace.get("runtime_error", ""),
            "exit_status": raw_trace.get("exit_status", 0),
            "execution_time_ms": exec_time,
            "memory_usage_kb": memory_usage,
        },
    }
