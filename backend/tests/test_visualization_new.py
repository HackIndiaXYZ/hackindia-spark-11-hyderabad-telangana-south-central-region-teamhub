"""Tests for the new universal code visualization modules."""
import pytest
import sys
import io
import math
from app.services.code_runner import run_and_trace
from app.services.algorithm_detector import detect_algorithm
from app.services.alternative_approaches import get_alternative_approaches, get_current_approach_complexity
from app.services.references_db import get_references
from app.services.trace_normalizer import normalize_trace


class TestCodeRunner:
    def test_run_basic_output(self):
        code = "print('hello')"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "hello" in output
        assert result["total_steps"] > 0

    def test_run_with_input(self):
        code = "numbers = list(map(int, input().split()))\nprint(max(numbers))"
        result = run_and_trace(code, "10 25 8 42 17")
        output = "".join(result.get("output_lines", []))
        assert "42" in output
        assert result["total_steps"] > 0

    def test_run_with_input_data(self):
        code = "numbers = list(map(int, input().split()))\nlargest = numbers[0]\nfor number in numbers:\n    if number > largest:\n        largest = number\nprint(largest)"
        result = run_and_trace(code, "10 25 8 42 17")
        output = "".join(result.get("output_lines", []))
        assert "42" in output

    def test_run_variable_tracking(self):
        code = "x = 5\ny = x + 3\nz = y * 2"
        result = run_and_trace(code)
        steps = result["steps"]
        final_vars = steps[-1]["variables"]
        assert len(steps) > 0

    def test_run_runtime_error(self):
        code = "x = 1/0"
        result = run_and_trace(code)
        assert result["runtime_error"]
        assert "ZeroDivisionError" in result["runtime_error"]

    def test_run_syntax_error(self):
        code = "if True"
        result = run_and_trace(code)
        assert result["compile_error"]

    def test_run_loop_tracking(self):
        code = "total = 0\nfor i in range(3):\n    total += i\nprint(total)"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "3" in output
        assert result["total_steps"] > 0

    def test_run_function_tracking(self):
        code = "def add(a, b):\n    return a + b\nresult = add(2, 3)\nprint(result)"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "5" in output
        assert result["total_steps"] > 0

    def test_normalize_trace(self):
        raw = {"steps": [{"step": 1, "line": 1, "operation": "start", "variables": {}}], "output_lines": ["hello\n"]}
        normalized = normalize_trace(raw)
        assert normalized["version"] == "1.0"
        assert normalized["total_steps"] == 1
        assert "hello" in normalized["program_output"]["stdout"]


class TestAlgorithmDetector:
    def test_detect_binary_search(self):
        code = "def binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1"
        result = detect_algorithm(code)
        assert "Binary Search" in result["detected"]
        assert result["confidence"] > 0

    def test_detect_two_pointers(self):
        code = "def two_sum(arr, target):\n    left = 0\n    right = len(arr) - 1\n    while left < right:\n        s = arr[left] + arr[right]\n        if s == target:\n            return [left, right]\n        elif s < target:\n            left += 1\n        else:\n            right -= 1\n    return []"
        result = detect_algorithm(code)
        assert "Two Pointers" in result["detected"] or "Two Pointers" in str(result)

    def test_detect_sliding_window(self):
        code = "def max_sum(arr, k):\n    window_sum = sum(arr[:k])\n    max_sum = window_sum\n    for i in range(k, len(arr)):\n        window_sum += arr[i] - arr[i - k]\n        max_sum = max(max_sum, window_sum)\n    return max_sum"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_hashing(self):
        code = "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_dp(self):
        code = "def fib(n):\n    dp = [0, 1]\n    for i in range(2, n + 1):\n        dp.append(dp[i-1] + dp[i-2])\n    return dp[n]"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_general_code(self):
        code = "print('hello world')"
        result = detect_algorithm(code)
        assert result["confidence"] == 0
        assert "General Iterative" in result["detected"]

    def test_detect_bfs(self):
        code = "def bfs(graph, start):\n    visited = set()\n    queue = [start]\n    while queue:\n        node = queue.pop(0)\n        if node not in visited:\n            visited.add(node)\n            queue.extend(graph[node])\n    return visited"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_all_detections_populated(self):
        code = "def sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr"
        result = detect_algorithm(code)
        assert len(result["all_detections"]) > 0


class TestAlternativeApproaches:
    def test_get_alternatives_for_linear_search(self):
        alts = get_alternative_approaches("Linear Search")
        assert len(alts) > 0
        names = [a["algorithm"] for a in alts]
        assert "Binary Search" in names or "Hash Map Lookup" in names

    def test_get_alternatives_for_sorting(self):
        alts = get_alternative_approaches("Bubble Sort")
        assert len(alts) > 0

    def test_get_alternatives_for_unknown(self):
        alts = get_alternative_approaches("Unknown Algorithm")
        assert alts == []

    def test_complexity_mapping(self):
        tc, sc = get_current_approach_complexity("Binary Search")
        assert tc == "O(log n)"
        assert sc == "O(1)"

    def test_default_complexity(self):
        tc, sc = get_current_approach_complexity("Nonexistent")
        assert tc is not None
        assert sc is not None


class TestReferencesDB:
    def test_get_references_exists(self):
        ref = get_references("Binary Search")
        assert ref["main_concept"] == "Divide and Conquer Search"
        assert len(ref["prerequisites"]) > 0
        assert len(ref["practice_problems"]) > 0

    def test_get_references_pseudocode(self):
        ref = get_references("Two Pointers")
        assert "left" in ref["pseudocode"]
        assert "right" in ref["pseudocode"]

    def test_get_references_fallback(self):
        ref = get_references("Nonexistent Algorithm")
        assert ref["main_concept"] == "General Programming"

    def test_references_for_all_known(self):
        algos = [
            "Linear Search", "Binary Search", "Bubble Sort", "Selection Sort",
            "Insertion Sort", "Merge Sort", "Quick Sort", "Two Pointers",
            "Sliding Window", "Prefix Sum", "Hashing / Hash Map", "Stack",
            "Queue", "Priority Queue / Heap", "Recursion", "Backtracking",
            "Divide and Conquer", "Greedy Algorithm", "Dynamic Programming",
            "Breadth-First Search", "Depth-First Search"
        ]
        for algo in algos:
            ref = get_references(algo)
            assert ref["main_concept"] != "General Programming", f"{algo} not found"


class TestVisualizationAPI:
    @pytest.mark.asyncio
    async def test_trace_endpoint(self, client):
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "print('hello')",
            "language": "python",
            "input_data": "",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["steps"]) > 0
        assert data["total_steps"] > 0
        assert "detection" in data
        assert "approaches" in data
        assert "references" in data
        assert "program_output" in data

    @pytest.mark.asyncio
    async def test_analyze_endpoint(self, client):
        resp = await client.post("/api/v1/visualization/analyze", json={
            "code": "def binary_search(arr, target):\n    low, high = 0, len(arr)-1\n    while low <= high:\n        mid = (low+high)//2\n        if arr[mid] == target: return mid\n        elif arr[mid] < target: low = mid+1\n        else: high = mid-1\n    return -1",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["detection"]["confidence"] > 0
        assert data["approaches"] is not None
        assert data["references"] is not None


class TestCodeRunnerEdgeCases:
    """Edge cases and error paths for code_runner."""

    def test_empty_code(self):
        result = run_and_trace("")
        assert result["total_steps"] > 0
        assert result["exit_status"] == 0

    def test_whitespace_only(self):
        result = run_and_trace("   \n  \n")
        assert result["total_steps"] > 0

    def test_multiline_output(self):
        code = "for i in range(3):\n    print(i)"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "0" in output and "1" in output and "2" in output

    def test_nested_function_call(self):
        code = "print(abs(-5))"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "5" in output

    def test_condition_true_branch(self):
        code = "x = 10\nif x > 5:\n    print('big')"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "big" in output
        assert result["total_steps"] > 0

    def test_condition_false_branch(self):
        code = "x = 2\nif x > 5:\n    print('big')\nelse:\n    print('small')"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "small" in output

    def test_while_loop_tracking(self):
        code = "i = 0\nwhile i < 3:\n    print(i)\n    i += 1"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "0" in output and "1" in output and "2" in output
        assert result["total_steps"] > 5

    def test_augmented_assignment(self):
        code = "x = 5\nx += 3\nprint(x)"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "8" in output

    def test_multiple_assignments(self):
        code = "a = b = c = 0\nprint(a)"
        result = run_and_trace(code)
        assert result["total_steps"] > 0

    def test_system_exit_handled(self):
        code = "import sys\nsys.exit(42)"
        result = run_and_trace(code)
        assert result["exit_status"] == 42

    def test_name_error(self):
        code = "print(undefined_var)"
        result = run_and_trace(code)
        assert "NameError" in result["runtime_error"]

    def test_type_error(self):
        code = "x = 'hello' + 42"
        result = run_and_trace(code)
        assert "TypeError" in result["runtime_error"]

    def test_value_error(self):
        code = "int('not_a_number')"
        result = run_and_trace(code)
        assert "ValueError" in result["runtime_error"]

    def test_index_error(self):
        code = "arr = [1, 2]\nprint(arr[10])"
        result = run_and_trace(code)
        assert "IndexError" in result["runtime_error"]

    def test_key_error(self):
        code = "d = {'a': 1}\nprint(d['b'])"
        result = run_and_trace(code)
        assert "KeyError" in result["runtime_error"]

    def test_unicode_code(self):
        code = "print('héllo wörld')"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "héllo wörld" in output

    def test_large_input(self):
        code = "print(sum([i for i in range(10)]))"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "45" in output

    def test_multiple_print_calls(self):
        code = "print('a')\nprint('b')\nprint('c')"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "a" in output and "b" in output and "c" in output

    def test_recursive_function(self):
        code = "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n-1)\nprint(fact(5))"
        result = run_and_trace(code)
        output = "".join(result.get("output_lines", []))
        assert "120" in output


class TestAlgorithmDetectorComprehensive:
    """Test all 32+ algorithm detection functions."""

    def test_detect_insertion_sort(self):
        code = "arr = [5,2,8]\nfor i in range(1, len(arr)):\n    key = arr[i]\n    j = i - 1\n    while j >= 0 and arr[j] > key:\n        arr[j+1] = arr[j]\n        j -= 1\n    arr[j+1] = key"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_selection_sort(self):
        code = "arr = [5,2,8]\nfor i in range(len(arr)):\n    min_idx = i\n    for j in range(i+1, len(arr)):\n        if arr[j] < arr[min_idx]:\n            min_idx = j\n    arr[i], arr[min_idx] = arr[min_idx], arr[i]"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_merge_sort(self):
        code = "def merge_sort(arr):\n    if len(arr) > 1:\n        mid = len(arr)//2\n        left = arr[:mid]\n        right = arr[mid:]\n        merge_sort(left)\n        merge_sort(right)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_quick_sort(self):
        code = "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[0]\n    left = [x for x in arr[1:] if x <= pivot]\n    right = [x for x in arr[1:] if x > pivot]\n    return quick_sort(left) + [pivot] + quick_sort(right)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_heap_sort(self):
        code = "def heapify(arr, n, i):\n    largest = i"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_counting_sort(self):
        code = "def counting_sort(arr):\n    count = [0] * (max(arr) + 1)\n    for v in arr:\n        count[v] += 1"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_stack(self):
        code = "stack = []\nstack.append(1)\nstack.pop()"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_queue(self):
        code = "from collections import deque\nq = deque()\nq.append(1)\nq.popleft()"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_monotonic_stack(self):
        code = "stack = []\nmonotonic = []\nwhile stack:\n    if stack[-1] > 5:\n        monotonic.append(stack.pop())"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_heap(self):
        code = "import heapq\nheap = []\nheappush(heap, 5)\nheappop(heap)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_recursion(self):
        code = "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_backtracking(self):
        code = "def backtrack(path, choices):\n    if len(path) == len(choices):\n        return [path]\n    result = []\n    for c in choices:\n        result.extend(backtrack(path+[c], choices))\n    return result"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_dfs(self):
        code = "def dfs(graph, start, visited):\n    visited.add(start)\n    for neighbor in graph[start]:\n        if neighbor not in visited:\n            dfs(graph, neighbor, visited)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_topological(self):
        code = "def topological_sort(graph):\n    indegree = {u:0 for u in graph}"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_dijkstra(self):
        code = "def dijkstra(graph, start):\n    import heapq\n    dist = {node: float('inf') for node in graph}"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_union_find(self):
        code = "def find(x):\n    if parent[x] != x:\n        parent[x] = find(parent[x])\n    return parent[x]\n\ndef union(x, y):\n    parent[find(x)] = find(y)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_trie(self):
        code = "class TrieNode:\n    def __init__(self):\n        self.children = {}\n        self.is_end = False"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_bit_manipulation(self):
        code = "x = 5\ny = x ^ 3\nz = x & y\nw = x | y"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_prefix_sum(self):
        code = "def prefix_sum(arr):\n    pref = [0]\n    for v in arr:\n        pref.append(pref[-1] + v)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_greedy(self):
        code = "def greedy_coin(coins, amount):\n    coins.sort(reverse=True)\n    count = 0\n    for c in coins:\n        while amount >= c:\n            amount -= c\n            count += 1\n    return count"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_divide_conquer(self):
        code = "def max_subarray(arr):\n    if len(arr) == 1:\n        return arr[0]\n    mid = len(arr) // 2\n    left = max_subarray(arr[:mid])\n    right = max_subarray(arr[mid:])"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_bellman_ford(self):
        code = "def bellman_ford(edges, V, start):\n    dist = [float('inf')] * V\n    dist[start] = 0\n    for _ in range(V-1):\n        for u, v, w in edges:\n            if dist[u] + w < dist[v]:\n                dist[v] = dist[u] + w"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_floyd_warshall(self):
        code = "def floyd_warshall(dist):\n    n = len(dist)\n    for k in range(n):\n        for i in range(n):\n            for j in range(n):\n                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_dp_memo(self):
        code = "from functools import lru_cache\n@lru_cache(maxsize=None)\ndef fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)"
        result = detect_algorithm(code)
        assert result["confidence"] > 0

    def test_detect_empty_code_returns_general(self):
        result = detect_algorithm("")
        assert result["confidence"] == 0
        assert "General" in result["detected"]


class TestAlternativeApproachesComprehensive:
    """Test all alternative approach entries exist and are well-formed."""

    def test_all_alternatives_have_required_fields(self):
        for algo, alts in {
            "Linear Search": get_alternative_approaches("Linear Search"),
            "Binary Search": get_alternative_approaches("Binary Search"),
            "Bubble Sort": get_alternative_approaches("Bubble Sort"),
            "Selection Sort": get_alternative_approaches("Selection Sort"),
            "Two Pointers": get_alternative_approaches("Two Pointers"),
            "Sliding Window": get_alternative_approaches("Sliding Window"),
            "Stack": get_alternative_approaches("Stack"),
            "Queue": get_alternative_approaches("Queue"),
            "Recursion": get_alternative_approaches("Recursion"),
            "Dynamic Programming": get_alternative_approaches("Dynamic Programming"),
            "Dijkstra's Algorithm": get_alternative_approaches("Dijkstra's Algorithm"),
            "Union-Find": get_alternative_approaches("Union-Find"),
            "Trie": get_alternative_approaches("Trie"),
            "Counting Sort": get_alternative_approaches("Counting Sort"),
        }.items():
            for alt in alts:
                assert "algorithm" in alt, f"{algo} missing algorithm"
                assert "time_complexity" in alt, f"{algo} missing time_complexity"
                assert "space_complexity" in alt, f"{algo} missing space_complexity"
                assert "explanation" in alt, f"{algo} missing explanation"
                assert alt["algorithm"], f"{algo} has empty algorithm"

    def test_complexity_mapping_all_known(self):
        known = [
            "Linear Search", "Binary Search", "Bubble Sort", "Selection Sort",
            "Insertion Sort", "Merge Sort", "Quick Sort", "Heap Sort",
            "Counting Sort", "Two Pointers", "Sliding Window", "Prefix Sum",
            "Hashing / Hash Map", "Stack", "Monotonic Stack", "Queue",
            "Priority Queue / Heap", "Recursion", "Backtracking",
            "Divide and Conquer", "Greedy Algorithm", "Dynamic Programming",
            "Breadth-First Search", "Depth-First Search", "Topological Sort",
            "Dijkstra's Algorithm", "Bellman-Ford Algorithm",
            "Floyd-Warshall Algorithm", "Union-Find", "Trie",
            "Bit Manipulation",
        ]
        for algo in known:
            tc, sc = get_current_approach_complexity(algo)
            assert tc is not None, f"{algo} time complexity is None"
            assert sc is not None, f"{algo} space complexity is None"

    def test_unknown_algorithm_returns_default_complexity(self):
        tc, sc = get_current_approach_complexity("Totally Made Up")
        assert tc is not None
        assert sc is not None


class TestReferencesDBComprehensive:
    """Test all 33 reference entries exist and are well-formed."""

    def test_all_references_have_required_fields(self):
        all_algos = [
            "Linear Search", "Binary Search", "Bubble Sort",
            "Selection Sort", "Insertion Sort", "Merge Sort",
            "Quick Sort", "Heap Sort", "Two Pointers", "Sliding Window",
            "Prefix Sum", "Hashing / Hash Map", "Stack", "Monotonic Stack",
            "Queue", "Priority Queue / Heap", "Recursion", "Backtracking",
            "Divide and Conquer", "Greedy Algorithm", "Dynamic Programming",
            "Breadth-First Search", "Depth-First Search", "Topological Sort",
            "Dijkstra's Algorithm", "Bellman-Ford Algorithm",
            "Floyd-Warshall Algorithm", "Union-Find", "Trie",
            "Bit Manipulation", "Counting Sort",
        ]
        for algo in all_algos:
            ref = get_references(algo)
            assert ref["main_concept"] != "General Programming", f"{algo} missing references"
            assert "pattern" in ref, f"{algo} missing pattern"
            assert "prerequisites" in ref, f"{algo} missing prerequisites"
            assert "similar_problems" in ref, f"{algo} missing similar_problems"
            assert "related_topics" in ref, f"{algo} missing related_topics"
            assert "practice_problems" in ref, f"{algo} missing practice_problems"
            assert "pseudocode" in ref, f"{algo} missing pseudocode"

    def test_nonexistent_algorithm_returns_fallback(self):
        ref = get_references("does_not_exist_12345")
        assert ref["main_concept"] == "General Programming"

    def test_all_references_have_non_empty_pseudocode(self):
        all_algos = [
            "Linear Search", "Binary Search", "Bubble Sort",
            "Selection Sort", "Insertion Sort", "Merge Sort",
            "Quick Sort", "Heap Sort", "Two Pointers", "Sliding Window",
            "Prefix Sum", "Hashing / Hash Map", "Stack", "Monotonic Stack",
            "Queue", "Priority Queue / Heap", "Recursion", "Backtracking",
            "Divide and Conquer", "Greedy Algorithm", "Dynamic Programming",
            "Breadth-First Search", "Depth-First Search", "Topological Sort",
            "Dijkstra's Algorithm", "Bellman-Ford Algorithm",
            "Floyd-Warshall Algorithm", "Union-Find", "Trie",
            "Bit Manipulation", "Counting Sort",
        ]
        for algo in all_algos:
            ref = get_references(algo)
            assert ref["pseudocode"], f"{algo} has empty pseudocode"


class TestTraceNormalizerEdgeCases:
    """Edge cases for trace_normalizer."""

    def test_empty_steps(self):
        result = normalize_trace({})
        assert result["total_steps"] == 0
        assert result["version"] == "1.0"

    def test_missing_fields(self):
        steps = [{"step": 1}]
        result = normalize_trace({"steps": steps})
        assert result["total_steps"] == 1
        assert result["steps"][0]["line"] == 1
        assert result["steps"][0]["operation"] == ""
        assert result["steps"][0]["variables"] == {}

    def test_with_full_trace_data(self):
        raw = {
            "steps": [
                {"step": 1, "line": 1, "operation": "start", "variables": {}},
                {"step": 2, "line": 2, "operation": "assign", "variables": {"x": 5},
                 "changedVariables": ["x"], "loopIteration": None, "conditionResult": None,
                 "callStack": [], "dataStructure": None, "highlightedIndexes": [],
                 "output": "", "explanation": "Assigning to x", "complexity": None},
            ],
            "output_lines": ["5\n"],
            "errors": [],
            "algorithm_type": "general",
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
            "compile_error": "",
            "runtime_error": "",
            "exit_status": 0,
            "execution_time_ms": 10,
            "memory_usage_kb": 100,
        }
        result = normalize_trace(raw)
        assert result["total_steps"] == 2
        assert result["program_output"]["stdout"] == "5\n"
        assert result["program_output"]["execution_time_ms"] == 10
        assert result["program_output"]["memory_usage_kb"] == 100

    def test_with_errors(self):
        raw = {
            "steps": [{"step": 1, "line": 1, "operation": "error", "variables": {}}],
            "output_lines": [],
            "errors": ["RuntimeError: test"],
        }
        result = normalize_trace(raw)
        assert result["program_output"]["stderr"] == "RuntimeError: test"


class TestVisualizationAPIEdgeCases:
    """Edge cases and error paths for the visualization API."""

    @pytest.mark.asyncio
    async def test_trace_empty_code(self, client):
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "",
            "language": "python",
        })
        data = resp.json()
        assert resp.status_code == 200
        assert data["total_steps"] >= 0

    @pytest.mark.asyncio
    async def test_trace_syntax_error(self, client):
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "if True",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["program_output"]["compile_error"]

    @pytest.mark.asyncio
    async def test_trace_runtime_error(self, client):
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "x = 1/0",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "ZeroDivisionError" in data["program_output"]["runtime_error"]

    @pytest.mark.asyncio
    async def test_trace_with_input(self, client):
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "print(input())",
            "language": "python",
            "input_data": "hello test",
        })
        assert resp.status_code == 200
        data = resp.json()
        output = data["program_output"]["stdout"]
        assert "hello test" in output

    @pytest.mark.asyncio
    async def test_trace_detection_enrichment(self, client):
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "arr = [1,2,3,4,5]\ntarget = 3\nlow, high = 0, len(arr)-1\nwhile low <= high:\n    mid = (low+high)//2\n    if arr[mid] == target: print('found')\n    elif arr[mid] < target: low = mid+1\n    else: high = mid-1",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["detection"]["confidence"] > 0

    @pytest.mark.asyncio
    async def test_analyze_empty_code(self, client):
        resp = await client.post("/api/v1/visualization/analyze", json={
            "code": "",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["detection"]["confidence"] == 0

    @pytest.mark.asyncio
    async def test_analyze_full_pipeline(self, client):
        resp = await client.post("/api/v1/visualization/analyze", json={
            "code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["detection"]["confidence"] > 0
        assert data["approaches"] is not None
        assert len(data["approaches"]["alternatives"]) > 0
        assert data["references"] is not None
        assert data["references"]["pseudocode"]

    @pytest.mark.asyncio
    async def test_end_to_end_code_execution(self, client):
        """End-to-end test: run actual code and verify output, detection, alternatives, references all populated."""
        resp = await client.post("/api/v1/visualization/trace", json={
            "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\nresult = factorial(5)\nprint(result)",
            "language": "python",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["steps"]) > 0
        assert "120" in data["program_output"]["stdout"]
        assert data["detection"]["confidence"] > 0
        assert data["references"] is not None
        assert data["references"]["main_concept"] != "General Programming"
