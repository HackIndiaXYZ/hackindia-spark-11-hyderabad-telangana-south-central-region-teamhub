import ast
import json
import re
from typing import Any


def generate_trace(code: str, language: str = "python", algorithm: str | None = None, input_data: str = "") -> dict:
    if language.lower() not in ("python", "py"):
        return _generate_generic_trace(code, algorithm)
    try:
        algo_type = algorithm or _detect_algorithm(code)
        if algo_type in ("bubble_sort", "selection_sort", "insertion_sort"):
            return _trace_sorting(code, algo_type, input_data)
        if algo_type in ("linear_search", "binary_search"):
            return _trace_searching(code, algo_type, input_data)
        if algo_type == "recursion":
            return _trace_recursion(code, input_data)
        if algo_type == "stack":
            return _trace_stack(code, input_data)
        if algo_type == "queue":
            return _trace_queue(code, input_data)
        if algo_type == "linked_list":
            return _trace_linked_list(code, input_data)
        if algo_type == "tree":
            return _trace_tree(code, input_data)
        if algo_type == "graph":
            return _trace_graph(code, input_data)
        if algo_type == "array":
            return _trace_array(code, input_data)
        return _trace_generic_python(code, algo_type, input_data)
    except Exception as e:
        return {
            "steps": [_make_step(1, 1, "error", {}, None, [], str(e))],
            "total_steps": 1,
            "algorithm_type": "error",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
        }


def _detect_algorithm(code: str) -> str:
    c = code.lower()
    if "bubble" in c or ("sort" in c and ("swap" in c or ("for" in c and "range" in c and c.count("for") >= 2))):
        return "bubble_sort"
    if "selection" in c and "sort" in c:
        return "selection_sort"
    if "insertion" in c and "sort" in c:
        return "insertion_sort"
    if "binary" in c and ("search" in c or "find" in c):
        return "binary_search"
    if "linear" in c and "search" in c:
        return "linear_search"
    if "search" in c or "find" in c:
        return "linear_search"
    if "factorial" in c or "fibonacci" in c or "def " in c and "return" in c and c.count("def ") > 1:
        return "recursion"
    if "stack" in c or ("push" in c and "pop" in c):
        return "stack"
    if "queue" in c or "enqueue" in c or "dequeue" in c:
        return "queue"
    if "linked" in c or "node" in c and ("next" in c or "prev" in c):
        return "linked_list"
    if "tree" in c or "binary" in c and ("left" in c or "right" in c):
        return "tree"
    if "graph" in c or "bfs" in c or "dfs" in c or "adjacent" in c or "neighbor" in c:
        return "graph"
    if "sort" in c:
        return "bubble_sort"
    return "general"


def _make_step(step: int, line: int, operation: str, variables: dict, data_structure: dict | None, highlighted: list[int], output: str = "", explanation: str = "", call_stack: list[str] | None = None, complexity: dict[str, str] | None = None) -> dict:
    return {
        "step": step,
        "line": line,
        "operation": operation,
        "variables": variables,
        "dataStructure": data_structure,
        "highlightedIndexes": highlighted,
        "callStack": call_stack or [],
        "output": output,
        "explanation": explanation,
        "complexity": complexity,
    }


def _trace_sorting(code: str, algo_type: str, input_data: str) -> dict:
    arr = _parse_array_input(input_data, code)
    steps: list[dict] = []
    line = 1
    step = 1

    steps.append(_make_step(step, line, "initialize", {"arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [], f"Initial array: {arr}", f"Starting {algo_type.replace('_', ' ')} with array {arr}"))
    step += 1

    if algo_type == "bubble_sort":
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                steps.append(_make_step(step, line + 1, "compare", {"i": i, "j": j, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [j, j + 1], "", f"Comparing {arr[j]} and {arr[j+1]} at positions {j} and {j+1}"))
                step += 1
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    steps.append(_make_step(step, line + 2, "swap", {"i": i, "j": j, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [j, j + 1], "", f"Swapped positions {j} and {j+1}: {arr[j]} and {arr[j+1]}"))
                    step += 1
        steps.append(_make_step(step, line, "complete", {"arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [], f"Sorted array: {arr}", "Array is now sorted", complexity={"time": "O(n^2)", "space": "O(1)"}))

    elif algo_type == "selection_sort":
        n = len(arr)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                steps.append(_make_step(step, line + 1, "compare", {"i": i, "j": j, "min_idx": min_idx, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [j, min_idx], "", f"Comparing {arr[j]} with current minimum {arr[min_idx]}"))
                step += 1
                if arr[j] < arr[min_idx]:
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                steps.append(_make_step(step, line + 2, "swap", {"i": i, "min_idx": min_idx, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [i, min_idx], "", f"Swapped {arr[min_idx]} and {arr[i]}"))
                step += 1
        steps.append(_make_step(step, line, "complete", {"arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [], f"Sorted array: {arr}", "Array is now sorted", complexity={"time": "O(n^2)", "space": "O(1)"}))

    elif algo_type == "insertion_sort":
        n = len(arr)
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            steps.append(_make_step(step, line + 1, "insert", {"key": key, "i": i, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [i], "", f"Inserting {key} into the sorted portion"))
            step += 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                steps.append(_make_step(step, line + 2, "shift", {"key": key, "i": i, "j": j, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [j, j + 1], "", f"Shifted {arr[j]} to the right"))
                step += 1
                j -= 1
            arr[j + 1] = key
            steps.append(_make_step(step, line + 3, "place", {"key": key, "i": i, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [j + 1], "", f"Placed {key} at position {j + 1}"))
            step += 1
        steps.append(_make_step(step, line, "complete", {"arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [], f"Sorted array: {arr}", "Array is now sorted", complexity={"time": "O(n^2)", "space": "O(1)"}))

    return {"steps": steps, "total_steps": len(steps), "algorithm_type": algo_type, "time_complexity": "O(n^2)", "space_complexity": "O(1)"}


def _trace_searching(code: str, algo_type: str, input_data: str) -> dict:
    arr = _parse_array_input(input_data, code)
    target = _parse_target_input(input_data, code, arr)
    steps: list[dict] = []
    line = 1
    step = 1
    steps.append(_make_step(step, line, "initialize", {"arr": arr.copy(), "target": target}, {"type": "array", "values": arr.copy()}, [], f"Searching for {target} in {arr}", f"Starting {algo_type.replace('_', ' ')} for target {target}"))
    step += 1

    if algo_type == "linear_search":
        for i in range(len(arr)):
            steps.append(_make_step(step, line + 1, "compare", {"i": i, "target": target, "current": arr[i]}, {"type": "array", "values": arr.copy()}, [i], "", f"Checking if {arr[i]} == {target}"))
            step += 1
            if arr[i] == target:
                steps.append(_make_step(step, line + 2, "found", {"i": i, "target": target}, {"type": "array", "values": arr.copy()}, [i], f"Found {target} at index {i}", f"Match found at index {i}!", complexity={"time": "O(n)", "space": "O(1)"}))
                return {"steps": steps, "total_steps": len(steps), "algorithm_type": algo_type, "time_complexity": "O(n)", "space_complexity": "O(1)"}
        steps.append(_make_step(step, line, "not_found", {"target": target}, {"type": "array", "values": arr.copy()}, [], f"{target} not found in array", f"Target {target} was not found", complexity={"time": "O(n)", "space": "O(1)"}))

    elif algo_type == "binary_search":
        low, high = 0, len(arr) - 1
        sorted_arr = sorted(arr)
        steps.append(_make_step(step, line, "sort", {"sorted_arr": sorted_arr}, {"type": "array", "values": sorted_arr.copy()}, [], f"Array sorted: {sorted_arr}", "Binary search requires a sorted array"))
        step += 1
        while low <= high:
            mid = (low + high) // 2
            steps.append(_make_step(step, line + 1, "compare", {"low": low, "high": high, "mid": mid, "current": sorted_arr[mid]}, {"type": "array", "values": sorted_arr.copy()}, [low, mid, high], "", f"Comparing {sorted_arr[mid]} with {target} (mid index: {mid})"))
            step += 1
            if sorted_arr[mid] == target:
                steps.append(_make_step(step, line + 2, "found", {"mid": mid, "target": target}, {"type": "array", "values": sorted_arr.copy()}, [mid], f"Found {target} at index {mid}", f"Match found at index {mid}!", complexity={"time": "O(log n)", "space": "O(1)"}))
                return {"steps": steps, "total_steps": len(steps), "algorithm_type": algo_type, "time_complexity": "O(log n)", "space_complexity": "O(1)"}
            elif sorted_arr[mid] < target:
                steps.append(_make_step(step, line + 3, "narrow_right", {"low": low, "high": high, "mid": mid}, {"type": "array", "values": sorted_arr.copy()}, list(range(mid + 1, high + 1)), "", f"{sorted_arr[mid]} < {target}, searching right half"))
                low = mid + 1
            else:
                steps.append(_make_step(step, line + 4, "narrow_left", {"low": low, "high": high, "mid": mid}, {"type": "array", "values": sorted_arr.copy()}, list(range(low, mid)), "", f"{sorted_arr[mid]} > {target}, searching left half"))
                high = mid - 1
            step += 1
        steps.append(_make_step(step, line, "not_found", {"target": target}, {"type": "array", "values": sorted_arr.copy()}, [], f"{target} not found", f"Target {target} was not found", complexity={"time": "O(log n)", "space": "O(1)"}))

    return {"steps": steps, "total_steps": len(steps), "algorithm_type": algo_type, "time_complexity": "O(n)" if algo_type == "linear_search" else "O(log n)", "space_complexity": "O(1)"}


def _trace_recursion(code: str, input_data: str) -> dict:
    n = _parse_int_input(input_data, code, default=5)
    steps: list[dict] = []
    step_counter = [0]
    call_stack: list[str] = []
    func_name = _extract_func_name(code) or "factorial"

    def recurse(val: int) -> int:
        step_counter[0] += 1
        call_stack.append(f"{func_name}({val})")
        steps.append(_make_step(step_counter[0], 1, "call", {"n": val, "result": None}, {"type": "call_stack", "values": call_stack.copy()}, [], "", f"Calling {func_name}({val})", call_stack=call_stack.copy()))
        if val <= 1:
            call_stack.pop()
            steps.append(_make_step(step_counter[0], 2, "base_case", {"n": val, "result": 1}, {"type": "call_stack", "values": call_stack.copy()}, [], f"Return 1", f"Base case reached: {func_name}({val}) returns 1", call_stack=call_stack.copy()))
            return 1
        result = val * recurse(val - 1)
        steps.append(_make_step(step_counter[0], 3, "return", {"n": val, "result": result}, {"type": "call_stack", "values": call_stack.copy()}, [], f"Return {result}", f"{func_name}({val}) returns {val} * {func_name}({val}-1) = {result}", call_stack=call_stack.copy()))
        call_stack.pop()
        return result

    result = recurse(n)
    steps.append(_make_step(step_counter[0] + 1, 1, "complete", {"final_result": result}, {"type": "call_stack", "values": []}, [], f"Final result: {result}", f"Completed: {func_name}({n}) = {result}", complexity={"time": "O(n)", "space": "O(n)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "recursion", "time_complexity": "O(n)", "space_complexity": "O(n)"}


def _trace_stack(code: str, input_data: str) -> dict:
    items = _parse_list_input(input_data, code, default=[10, 20, 30])
    steps: list[dict] = []
    stack: list[int] = []
    step = 1

    steps.append(_make_step(step, 1, "initialize", {"stack": []}, {"type": "stack", "values": []}, [], "Empty stack created", "Starting with an empty stack"))
    step += 1

    for item in items:
        stack.append(item)
        steps.append(_make_step(step, 2, "push", {"value": item, "stack": stack.copy()}, {"type": "stack", "values": stack.copy()}, [], f"Pushed {item}", f"Pushed {item} onto the stack. Top is now {item}"))
        step += 1

    for _ in range(min(len(stack), 2)):
        val = stack.pop()
        steps.append(_make_step(step, 3, "pop", {"value": val, "stack": stack.copy()}, {"type": "stack", "values": stack.copy()}, [], f"Popped {val}", f"Popped {val} from the stack. Top is now {stack[-1] if stack else 'empty'}"))
        step += 1

    steps.append(_make_step(step, 1, "complete", {"stack": stack.copy()}, {"type": "stack", "values": stack.copy()}, [], f"Final stack: {stack}", f"Stack operations complete. Remaining: {stack}", complexity={"time": "O(1) per op", "space": "O(n)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "stack", "time_complexity": "O(1) per op", "space_complexity": "O(n)"}


def _trace_queue(code: str, input_data: str) -> dict:
    items = _parse_list_input(input_data, code, default=[10, 20, 30])
    steps: list[dict] = []
    queue: list[int] = []
    step = 1

    steps.append(_make_step(step, 1, "initialize", {"queue": []}, {"type": "queue", "values": []}, [], "Empty queue created", "Starting with an empty queue"))
    step += 1

    for item in items:
        queue.append(item)
        steps.append(_make_step(step, 2, "enqueue", {"value": item, "queue": queue.copy()}, {"type": "queue", "values": queue.copy()}, [], f"Enqueued {item}", f"Added {item} to the back of the queue"))
        step += 1

    for _ in range(min(len(queue), 2)):
        val = queue.pop(0)
        steps.append(_make_step(step, 3, "dequeue", {"value": val, "queue": queue.copy()}, {"type": "queue", "values": queue.copy()}, [], f"Dequeued {val}", f"Removed {val} from the front of the queue"))
        step += 1

    steps.append(_make_step(step, 1, "complete", {"queue": queue.copy()}, {"type": "queue", "values": queue.copy()}, [], f"Final queue: {queue}", f"Queue operations complete. Remaining: {queue}", complexity={"time": "O(1) per op", "space": "O(n)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "queue", "time_complexity": "O(1) per op", "space_complexity": "O(n)"}


def _trace_linked_list(code: str, input_data: str) -> dict:
    items = _parse_list_input(input_data, code, default=[10, 20, 30])
    steps: list[dict] = []
    linked: list[int] = []
    step = 1

    steps.append(_make_step(step, 1, "initialize", {"list": []}, {"type": "linked_list", "values": []}, [], "Empty linked list", "Starting with an empty linked list"))
    step += 1

    for item in items:
        linked.append(item)
        steps.append(_make_step(step, 2, "insert", {"value": item, "list": linked.copy()}, {"type": "linked_list", "values": linked.copy()}, [len(linked) - 1], f"Inserted {item}", f"Inserted {item} at the tail"))
        step += 1

    if linked:
        mid = len(linked) // 2
        steps.append(_make_step(step, 3, "access", {"index": mid, "value": linked[mid]}, {"type": "linked_list", "values": linked.copy()}, [mid], f"Accessed index {mid}: {linked[mid]}", f"Traversed to index {mid} to access value {linked[mid]}"))
        step += 1

    steps.append(_make_step(step, 1, "complete", {"list": linked.copy()}, {"type": "linked_list", "values": linked.copy()}, [], f"Final list: {linked}", "Linked list operations complete", complexity={"time": "O(n)", "space": "O(n)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "linked_list", "time_complexity": "O(n)", "space_complexity": "O(n)"}


def _trace_tree(code: str, input_data: str) -> dict:
    values = _parse_list_input(input_data, code, default=[4, 2, 6, 1, 3, 5, 7])
    steps: list[dict] = []
    step = 1

    steps.append(_make_step(step, 1, "initialize", {"root": None}, {"type": "tree", "values": [], "root": None}, [], "Empty tree", "Starting with an empty binary search tree"))
    step += 1

    tree_nodes: list[int] = []
    for val in values:
        tree_nodes.append(val)
        steps.append(_make_step(step, 2, "insert", {"value": val, "tree": tree_nodes.copy()}, {"type": "tree", "values": tree_nodes.copy(), "root": tree_nodes[0] if tree_nodes else None}, [len(tree_nodes) - 1], f"Inserted {val}", f"Inserted {val} into the BST"))
        step += 1

    steps.append(_make_step(step, 3, "inorder", {"tree": tree_nodes.copy()}, {"type": "tree", "values": sorted(tree_nodes), "root": tree_nodes[0] if tree_nodes else None}, list(range(len(tree_nodes))), f"In-order: {sorted(tree_nodes)}", "In-order traversal gives sorted order", complexity={"time": "O(n log n)", "space": "O(n)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "tree", "time_complexity": "O(n log n)", "space_complexity": "O(n)"}


def _trace_graph(code: str, input_data: str) -> dict:
    steps: list[dict] = []
    step = 1
    nodes = ["A", "B", "C", "D", "E"]
    edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "E"), ("D", "E")]

    steps.append(_make_step(step, 1, "initialize", {"nodes": nodes, "edges": edges}, {"type": "graph", "nodes": nodes, "edges": edges}, [], f"Graph: {nodes}", "Starting graph traversal"))
    step += 1

    visited: list[str] = []
    queue_gr: list[str] = ["A"]
    steps.append(_make_step(step, 2, "visit", {"current": "A", "visited": visited.copy(), "queue": queue_gr.copy()}, {"type": "graph", "nodes": nodes, "edges": edges, "visited": visited.copy(), "current": "A"}, [], "Visit A", "Start BFS from node A"))
    step += 1

    while queue_gr:
        current = queue_gr.pop(0)
        if current in visited:
            continue
        visited.append(current)
        for u, v in edges:
            if u == current and v not in visited and v not in queue_gr:
                queue_gr.append(v)
            elif v == current and u not in visited and u not in queue_gr:
                queue_gr.append(u)
        steps.append(_make_step(step, 3, "explore", {"current": current, "visited": visited.copy(), "queue": queue_gr.copy()}, {"type": "graph", "nodes": nodes, "edges": edges, "visited": visited.copy(), "current": current}, [], f"Visited: {visited}", f"Explored neighbors of {current}, queue: {queue_gr}"))
        step += 1

    steps.append(_make_step(step, 1, "complete", {"visited": visited}, {"type": "graph", "nodes": nodes, "edges": edges, "visited": visited, "current": None}, [], f"Traversal order: {visited}", f"BFS complete: {' -> '.join(visited)}", complexity={"time": "O(V + E)", "space": "O(V)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "graph", "time_complexity": "O(V + E)", "space_complexity": "O(V)"}


def _trace_array(code: str, input_data: str) -> dict:
    arr = _parse_array_input(input_data, code)
    steps: list[dict] = []
    step = 1

    steps.append(_make_step(step, 1, "initialize", {"arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [], f"Array: {arr}", "Array initialized"))
    step += 1

    for i, val in enumerate(arr):
        steps.append(_make_step(step, 2, "access", {"index": i, "value": val, "arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [i], f"arr[{i}] = {val}", f"Accessing element at index {i}, value is {val}"))
        step += 1

    steps.append(_make_step(step, 1, "complete", {"arr": arr.copy()}, {"type": "array", "values": arr.copy()}, [], f"Array traversal complete", "All elements accessed", complexity={"time": "O(n)", "space": "O(1)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": "array", "time_complexity": "O(n)", "space_complexity": "O(1)"}


def _trace_generic_python(code: str, algo_type: str, input_data: str) -> dict:
    steps: list[dict] = []
    step = 1
    variables: dict[str, Any] = {}
    call_stack: list[str] = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"steps": [_make_step(1, 1, "error", {}, None, [], "Syntax error in code")], "total_steps": 1, "algorithm_type": algo_type, "time_complexity": "N/A", "space_complexity": "N/A"}

    lines = code.split("\n")
    steps.append(_make_step(step, 1, "start", {}, None, [], "", "Code execution started"))
    step += 1

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            func_args = [arg.arg for arg in node.args.args]
            call_stack.append(f"{func_name}()")
            steps.append(_make_step(step, node.lineno, "define_function", {"function": func_name, "args": func_args}, None, [], "", f"Defining function {func_name}({', '.join(func_args)})", call_stack=call_stack.copy()))
            step += 1
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables[target.id] = "<value>"
            steps.append(_make_step(step, node.lineno, "assign", variables.copy(), None, [], "", f"Assigned: {', '.join(variables.keys())}"))
            step += 1
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func_name_str = ""
            if isinstance(node.value.func, ast.Name):
                func_name_str = node.value.func.id
            elif isinstance(node.value.func, ast.Attribute):
                func_name_str = node.value.func.attr
            steps.append(_make_step(step, node.lineno, "call", variables.copy(), None, [], "", f"Calling {func_name_str}()"))
            step += 1
        elif isinstance(node, ast.For) or isinstance(node, ast.While):
            loop_type = "for" if isinstance(node, ast.For) else "while"
            steps.append(_make_step(step, getattr(node, "lineno", 1), "loop_start", variables.copy(), None, [], "", f"Starting {loop_type} loop"))
            step += 1
        elif isinstance(node, ast.If):
            steps.append(_make_step(step, node.lineno, "condition", variables.copy(), None, [], "", "Evaluating conditional"))
            step += 1
        elif isinstance(node, ast.Return):
            steps.append(_make_step(step, node.lineno, "return", variables.copy(), None, [], "", "Returning from function"))
            step += 1

    steps.append(_make_step(step, len(lines), "complete", variables.copy(), None, [], "", "Execution complete", complexity={"time": "O(n)", "space": "O(n)"}))
    return {"steps": steps, "total_steps": len(steps), "algorithm_type": algo_type, "time_complexity": "O(n)", "space_complexity": "O(n)"}


def _generate_generic_trace(code: str, algorithm: str | None) -> dict:
    steps = [
        _make_step(1, 1, "start", {}, None, [], "", "Code received (non-Python language)"),
        _make_step(2, 1, "info", {}, None, [], "", "Visualization currently supports Python. The code has been received for display purposes."),
    ]
    return {"steps": steps, "total_steps": 2, "algorithm_type": algorithm or "unsupported", "time_complexity": "N/A", "space_complexity": "N/A"}


def _parse_array_input(input_data: str, code: str) -> list[int]:
    if input_data:
        try:
            parsed = json.loads(input_data)
            if isinstance(parsed, list):
                return [int(x) for x in parsed]
        except (json.JSONDecodeError, ValueError):
            pass
        nums = [int(x) for x in input_data.replace("[", "").replace("]", "").split(",") if x.strip().isdigit() or (x.strip().lstrip("-").isdigit())]
        if nums:
            return nums
    arrays = re.findall(r'\[([0-9,\s\-]+)\]', code)
    if arrays:
        try:
            nums = [int(x.strip()) for x in arrays[0].split(",") if x.strip()]
            if nums:
                return nums
        except ValueError:
            pass
    return [5, 2, 8, 1, 9, 3]


def _parse_target_input(input_data: str, code: str, arr: list[int]) -> int:
    if input_data:
        try:
            parsed = json.loads(input_data)
            if isinstance(parsed, dict) and "target" in parsed:
                return int(parsed["target"])
            if isinstance(parsed, dict) and "search" in parsed:
                return int(parsed["search"])
        except (json.JSONDecodeError, ValueError):
            pass
        nums = [int(x.strip()) for x in input_data.replace("[", "").replace("]", "").split(",") if x.strip().lstrip("-").isdigit()]
        if len(nums) > 1:
            return nums[-1]
    targets = re.findall(r'target\s*=\s*(\d+)', code)
    if targets:
        return int(targets[0])
    return arr[len(arr) // 2] if arr else 5


def _parse_int_input(input_data: str, code: str, default: int = 5) -> int:
    if input_data:
        try:
            parsed = json.loads(input_data)
            if isinstance(parsed, int):
                return parsed
            if isinstance(parsed, dict) and "n" in parsed:
                return int(parsed["n"])
        except (json.JSONDecodeError, ValueError):
            pass
        nums = [int(x) for x in input_data.split() if x.isdigit()]
        if nums:
            return nums[0]
    n_match = re.search(r'n\s*=\s*(\d+)', code)
    if n_match:
        return int(n_match.group(1))
    return default


def _parse_list_input(input_data: str, code: str, default: list[int] | None = None) -> list[int]:
    if default is None:
        default = [10, 20, 30]
    if input_data:
        try:
            parsed = json.loads(input_data)
            if isinstance(parsed, list):
                return [int(x) for x in parsed]
        except (json.JSONDecodeError, ValueError):
            pass
    arrays = re.findall(r'\[([0-9,\s]+)\]', code)
    if arrays:
        try:
            nums = [int(x.strip()) for x in arrays[0].split(",") if x.strip()]
            if nums:
                return nums
        except ValueError:
            pass
    return default


def _extract_func_name(code: str) -> str | None:
    match = re.search(r'def\s+(\w+)', code)
    return match.group(1) if match else None
