import re


def detect_algorithm(code: str) -> dict:
    c = code.lower()
    results = []

    checks = [
        ("Linear Search", _check_linear_search, "Iterates through elements sequentially to find a target."),
        ("Binary Search", _check_binary_search, "Divides search space in half by comparing with middle element."),
        ("Bubble Sort", _check_bubble_sort, "Repeatedly swaps adjacent elements if they are in wrong order."),
        ("Selection Sort", _check_selection_sort, "Repeatedly selects minimum element and places it at correct position."),
        ("Insertion Sort", _check_insertion_sort, "Builds sorted array by inserting elements into their correct positions."),
        ("Merge Sort", _check_merge_sort, "Divides array into halves, recursively sorts, then merges."),
        ("Quick Sort", _check_quick_sort, "Picks a pivot and partitions array around it recursively."),
        ("Heap Sort", _check_heap_sort, "Uses heap data structure to extract elements in sorted order."),
        ("Counting Sort", _check_counting_sort, "Counts occurrences of each value to determine positions."),
        ("Two Pointers", _check_two_pointers, "Uses two pointers moving towards each other to solve the problem."),
        ("Sliding Window", _check_sliding_window, "Maintains a window that slides through the array."),
        ("Prefix Sum", _check_prefix_sum, "Precomputes cumulative sums for range query optimization."),
        ("Hashing / Hash Map", _check_hashing, "Uses a hash map to store and retrieve values efficiently."),
        ("Stack", _check_stack, "Uses LIFO stack for ordered operations."),
        ("Monotonic Stack", _check_monotonic_stack, "Maintains stack with monotonically increasing or decreasing values."),
        ("Queue", _check_queue, "Uses FIFO queue for ordered operations."),
        ("Priority Queue / Heap", _check_heap, "Uses heap for priority-based extraction."),
        ("Recursion", _check_recursion, "Function calls itself to solve smaller subproblems."),
        ("Backtracking", _check_backtracking, "Explores possibilities recursively, backtracking when constraints fail."),
        ("Divide and Conquer", _check_divide_conquer, "Divides problem into subproblems, solves, and combines."),
        ("Greedy Algorithm", _check_greedy, "Makes locally optimal choices at each step."),
        ("Dynamic Programming", _check_dp, "Stores subproblem results to avoid recomputation."),
        ("Breadth-First Search", _check_bfs, "Explores level by level using a queue."),
        ("Depth-First Search", _check_dfs, "Explores depth-first using recursion or stack."),
        ("Topological Sort", _check_topological, "Orders nodes in directed acyclic graph linearly."),
        ("Dijkstra's Algorithm", _check_dijkstra, "Finds shortest paths using priority queue."),
        ("Bellman-Ford Algorithm", _check_bellman_ford, "Finds shortest paths tolerating negative edges."),
        ("Floyd-Warshall Algorithm", _check_floyd_warshall, "Computes shortest paths between all pairs."),
        ("Union-Find", _check_union_find, "Manages disjoint sets with union and find operations."),
        ("Trie", _check_trie, "Uses prefix tree for string operations."),
        ("Bit Manipulation", _check_bit_manipulation, "Uses bitwise operations for efficient computation."),
    ]

    for name, check_fn, reason in checks:
        score = check_fn(code, c)
        if score > 0:
            results.append((name, score, reason))

    if not results:
        return {
            "detected": "General Iterative Approach",
            "confidence": 0,
            "reason": "The code does not strongly match a known algorithmic pattern.",
            "all_detections": [],
        }

    results.sort(key=lambda x: -x[1])
    top = results[0]
    confidence = min(100, int(top[1] * 100))

    return {
        "detected": top[0],
        "confidence": confidence,
        "reason": top[2],
        "all_detections": [{"name": n, "score": s} for n, s, _ in results],
    }


def _check_linear_search(code: str, c: str) -> float:
    score = 0.0
    if "for" in c and "range" in c:
        if "target" in c or "search" in c or "find" in c:
            score += 0.4
        if "==" in c or "return" in c:
            score += 0.3
        if ("if arr" in c or "if " in c) and "==" in c:
            score += 0.3
    return min(1.0, score)


def _check_binary_search(code: str, c: str) -> float:
    score = 0.0
    if "low" in c and "high" in c and "mid" in c:
        score += 0.5
    if "binary" in c or "while low" in c:
        score += 0.2
    if "mid = " in c and ("+ high" in c or "low +" in c):
        score += 0.3
    return min(1.0, score)


def _check_bubble_sort(code: str, c: str) -> float:
    score = 0.0
    if "bubble" in c:
        score += 0.5
    nested_loops = c.count("for") >= 2
    if nested_loops and "swap" in c:
        score += 0.4
    if nested_loops and "arr[j]" in c and "arr[j+1]" in c:
        score += 0.3
    return min(1.0, score)


def _check_selection_sort(code: str, c: str) -> float:
    score = 0.0
    if "selection" in c:
        score += 0.5
    if "min_idx" in c or "min_index" in c or "minindex" in c:
        score += 0.3
    if "swap" in c and "min" in c:
        score += 0.2
    return min(1.0, score)


def _check_insertion_sort(code: str, c: str) -> float:
    score = 0.0
    if "insertion" in c:
        score += 0.5
    if "key" in c and "while" in c:
        score += 0.3
    if "j >= 0" in c or "j>-1" in c:
        score += 0.2
    return min(1.0, score)


def _check_merge_sort(code: str, c: str) -> float:
    score = 0.0
    if "merge" in c and "sort" in c:
        score += 0.5
    if "def merge" in c:
        score += 0.3
    if "mid" in c and "left" in c and "right" in c and "merge" in c:
        score += 0.2
    return min(1.0, score)


def _check_quick_sort(code: str, c: str) -> float:
    score = 0.0
    if "quick" in c and "sort" in c:
        score += 0.5
    if "pivot" in c:
        score += 0.3
    if "partition" in c:
        score += 0.2
    return min(1.0, score)


def _check_heap_sort(code: str, c: str) -> float:
    score = 0.0
    if "heap" in c and "sort" in c:
        score += 0.5
    if "heapify" in c:
        score += 0.3
    if "heap" in c and "pop" in c:
        score += 0.2
    return min(1.0, score)


def _check_counting_sort(code: str, c: str) -> float:
    score = 0.0
    if "count" in c and "sort" in c:
        score += 0.5
    if "count" in c and ("max" in c or "freq" in c):
        score += 0.3
    return min(1.0, score)


def _check_two_pointers(code: str, c: str) -> float:
    score = 0.0
    if "left" in c and "right" in c:
        score += 0.3
    if "while left" in c or "while l <" in c:
        score += 0.3
    if "left += 1" in c or "left +=" in c or "right -= 1" in c or "right -=" in c:
        score += 0.2
    if "right" in c and "left" in c and "two" in c:
        score += 0.2
    return min(1.0, score)


def _check_sliding_window(code: str, c: str) -> float:
    score = 0.0
    if "window" in c:
        score += 0.4
    if "right" in c and "left" in c and "while" in c:
        score += 0.3
    if "subarray" in c or "substring" in c:
        score += 0.2
    if "count" in c and "window" in c:
        score += 0.2
    return min(1.0, score)


def _check_prefix_sum(code: str, c: str) -> float:
    score = 0.0
    if "prefix" in c:
        score += 0.5
    if "cumulative" in c or "running" in c:
        score += 0.3
    if "pref" in c and "sum" in c:
        score += 0.2
    return min(1.0, score)


def _check_hashing(code: str, c: str) -> float:
    score = 0.0
    if "dict" in c or "defaultdict" in c or "Counter" in c:
        score += 0.4
    if "hash" in c or "map" in c:
        score += 0.2
    if "{}" in c or "set(" in c:
        score += 0.2
    if "in" in c and ("if " in c or "while " in c):
        score += 0.2
    return min(1.0, score)


def _check_stack(code: str, c: str) -> float:
    score = 0.0
    if "stack" in c:
        score += 0.4
    if "append" in c and ("pop" in c or "pop(" in c):
        score += 0.3
    if "push" in c and "pop" in c:
        score += 0.3
    return min(1.0, score)


def _check_monotonic_stack(code: str, c: str) -> float:
    score = 0.0
    if "monotonic" in c:
        score += 0.6
    if "stack" in c and "while stack" in c:
        score += 0.3
    return min(1.0, score)


def _check_queue(code: str, c: str) -> float:
    score = 0.0
    if "queue" in c:
        score += 0.4
    if "deque" in c or "deque(" in c:
        score += 0.3
    if "popleft" in c or "pop(0)" in c:
        score += 0.3
    return min(1.0, score)


def _check_heap(code: str, c: str) -> float:
    score = 0.0
    if "heapq" in c:
        score += 0.4
    if "heappush" in c or "heappop" in c:
        score += 0.4
    if "heap" in c and ("push" in c or "pop" in c):
        score += 0.3
    return min(1.0, score)


def _check_recursion(code: str, c: str) -> float:
    score = 0.0
    defs = re.findall(r'def (\w+)', code)
    if len(defs) >= 1:
        for d in defs:
            if d in code[code.find(f"def {d}") + len(d) + 10:]:
                score += 0.6
                break
    if len(defs) >= 2:
        score += 0.2
    if "factorial" in c or "fibonacci" in c or "backtrack" in c:
        score += 0.2
    return min(1.0, score)


def _check_backtracking(code: str, c: str) -> float:
    score = 0.0
    if "backtrack" in c:
        score += 0.6
    if "def solve" in c and "def" in c and ("return" in c or "recursive" in c):
        score += 0.2
    if "prune" in c or "candidate" in c:
        score += 0.2
    return min(1.0, score)


def _check_divide_conquer(code: str, c: str) -> float:
    score = 0.0
    if "divide" in c and "conquer" in c:
        score += 0.5
    if "mid" in c and "left" in c and "right" in c and "merge" in c:
        score += 0.3
    return min(1.0, score)


def _check_greedy(code: str, c: str) -> float:
    score = 0.0
    if "greedy" in c:
        score += 0.5
    if "sort" in c and ("largest" in c or "smallest" in c or "minimum" in c or "maximum" in c):
        score += 0.3
    if "if " in c and ("optimal" in c or "best" in c or "local" in c):
        score += 0.2
    return min(1.0, score)


def _check_dp(code: str, c: str) -> float:
    score = 0.0
    if "dp" in c or "memo" in c:
        score += 0.4
    if "lru_cache" in c or "functools" in c:
        score += 0.3
    if "max(" in c and "dp" in c:
        score += 0.1
    if "min(" in c and "dp" in c:
        score += 0.1
    return min(1.0, score)


def _check_bfs(code: str, c: str) -> float:
    score = 0.0
    if "bfs" in c:
        score += 0.5
    if "queue" in c and "while" in c and ("pop" in c or "popleft" in c):
        score += 0.3
    if "visited" in c and "queue" in c:
        score += 0.2
    return min(1.0, score)


def _check_dfs(code: str, c: str) -> float:
    score = 0.0
    if "dfs" in c:
        score += 0.5
    if "visited" in c and ("stack" in c or "recursive" in c or "def dfs" in c):
        score += 0.3
    if "adj" in c or "neighbor" in c:
        score += 0.2
    return min(1.0, score)


def _check_topological(code: str, c: str) -> float:
    score = 0.0
    if "topological" in c:
        score += 0.5
    if "indegree" in c or "in_degree" in c:
        score += 0.3
    if "kahn" in c or "topo" in c:
        score += 0.2
    return min(1.0, score)


def _check_dijkstra(code: str, c: str) -> float:
    score = 0.0
    if "dijkstra" in c:
        score += 0.5
    if "heapq" in c and "dist" in c:
        score += 0.3
    if "shortest" in c:
        score += 0.2
    return min(1.0, score)


def _check_bellman_ford(code: str, c: str) -> float:
    score = 0.0
    if "bellman" in c or "ford" in c:
        score += 0.5
    if "relax" in c and "edge" in c:
        score += 0.3
    if "shortest" in c and "negative" in c:
        score += 0.2
    return min(1.0, score)


def _check_floyd_warshall(code: str, c: str) -> float:
    score = 0.0
    if "floyd" in c or "warshall" in c:
        score += 0.5
    if "for k" in c and "for i" in c and "for j" in c:
        score += 0.3
    return min(1.0, score)


def _check_union_find(code: str, c: str) -> float:
    score = 0.0
    if "union" in c and "find" in c:
        score += 0.4
    if "def find" in c or "def union" in c:
        score += 0.3
    if "parent" in c and ("rank" in c or "size" in c):
        score += 0.3
    return min(1.0, score)


def _check_trie(code: str, c: str) -> float:
    score = 0.0
    if "trie" in c or "prefix" in c:
        score += 0.4
    if "children" in c and ("insert" in c or "search" in c or "starts" in c):
        score += 0.3
    if "class" in c and ("node" in c or "trie" in c):
        score += 0.3
    return min(1.0, score)


def _check_bit_manipulation(code: str, c: str) -> float:
    score = 0.0
    if "&" in code or "|" in code or "^" in code:
        score += 0.3
    if "<<" in code or ">>" in code:
        score += 0.3
    if " & " in code and "| " in code:
        score += 0.2
    if "bit" in c or "xor" in c:
        score += 0.2
    return min(1.0, score)
