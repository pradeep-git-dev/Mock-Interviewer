"""
Advanced DSA questions with code snippets and debugging tasks.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import random


@dataclass(frozen=True)
class AdvancedQuestion:
    qid: int
    topic: str
    difficulty: str  # Easy, Medium, Hard
    question_type: str  # "snippet" or "debug"
    prompt: str
    code_snippet: str
    language: str  # python, java, cpp
    expected_output: str
    hints: List[str]
    correct_answer: str  # explanation or fixed code


def get_advanced_bank() -> List[AdvancedQuestion]:
    return [
        # ─── ARRAYS ───
        AdvancedQuestion(101, "Arrays", "Easy", "snippet",
            "What will this code print? Explain why.",
            "arr = [1, 2, 3, 4, 5]\nresult = arr[1:4]\nprint(result)",
            "python", "[2, 3, 4]",
            ["Slicing is exclusive of the end index"],
            "It prints [2, 3, 4]. Python slicing arr[1:4] takes elements at indices 1, 2, 3."),

        AdvancedQuestion(102, "Arrays", "Medium", "debug",
            "This function should return the second largest element. Find and fix the bug.",
            "def second_largest(arr):\n    largest = arr[0]\n    second = arr[0]  # BUG\n    for num in arr:\n        if num > largest:\n            second = largest\n            largest = num\n        elif num > second:\n            second = num\n    return second",
            "python", "The second largest element",
            ["What if all elements equal largest?", "Initialize second differently"],
            "Bug: second is initialized to arr[0] same as largest. If arr[0] is the largest, second never updates correctly. Fix: initialize second to float('-inf') or handle duplicates."),

        AdvancedQuestion(103, "Arrays", "Medium", "snippet",
            "What is the time complexity of this code? What does it compute?",
            "def mystery(arr):\n    n = len(arr)\n    max_sum = arr[0]\n    cur_sum = arr[0]\n    for i in range(1, n):\n        cur_sum = max(arr[i], cur_sum + arr[i])\n        max_sum = max(max_sum, cur_sum)\n    return max_sum",
            "python", "Maximum subarray sum (Kadane's algorithm)",
            ["This is a well-known algorithm", "Think about contiguous subarrays"],
            "This is Kadane's Algorithm for Maximum Subarray Sum. Time complexity is O(n). It decides at each step whether to extend the current subarray or start fresh."),

        # ─── STRINGS ───
        AdvancedQuestion(104, "Strings", "Easy", "snippet",
            "What does this function return for input 'racecar'?",
            "def check(s):\n    return s == s[::-1]",
            "python", "True",
            ["s[::-1] reverses the string"],
            "It checks if the string is a palindrome. 'racecar' reversed is 'racecar', so it returns True."),

        AdvancedQuestion(105, "Strings", "Medium", "debug",
            "This function should count vowels in a string. Fix the bug.",
            "def count_vowels(s):\n    count = 0\n    vowels = 'aeiou'\n    for char in s:\n        if char in vowels:\n            count += 1\n    return count  # Fails for 'HELLO'",
            "python", "Works for uppercase too",
            ["What about uppercase vowels?"],
            "Bug: Only checks lowercase vowels. Fix: change to `if char.lower() in vowels:` or add uppercase vowels to the set."),

        # ─── LINKED LISTS ───
        AdvancedQuestion(106, "Linked Lists", "Medium", "snippet",
            "What does this code do? What is the final state of the list?",
            "class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef mystery(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev",
            "python", "Reverses the linked list",
            ["Track what happens to each pointer"],
            "This reverses a singly linked list in-place. It iterates through the list, reversing each node's next pointer. Time: O(n), Space: O(1)."),

        AdvancedQuestion(107, "Linked Lists", "Hard", "debug",
            "This function should detect a cycle in a linked list. Find the bug.",
            "def has_cycle(head):\n    slow = head\n    fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next  # BUG\n        if slow == fast:\n            return True\n    return False",
            "python", "True if cycle exists",
            ["Fast pointer should move 2 steps"],
            "Bug: fast moves only 1 step (fast = fast.next). It should move 2 steps: fast = fast.next.next. Without this, slow and fast move at the same speed and the algorithm fails."),

        # ─── STACKS & QUEUES ───
        AdvancedQuestion(108, "Stacks", "Medium", "snippet",
            "What does this function return for input '({[]})'? Explain the algorithm.",
            "def is_valid(s):\n    stack = []\n    mapping = {')':'(', '}':'{', ']':'['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top:\n                return False\n        else:\n            stack.append(char)\n    return not stack",
            "python", "True",
            ["It uses a stack to match brackets"],
            "This validates balanced parentheses using a stack. For '({[]})': each opening bracket is pushed, each closing bracket pops and checks for a match. Returns True because all brackets are balanced."),

        AdvancedQuestion(109, "Queues", "Medium", "debug",
            "This BFS should find shortest path in a grid. Fix the bug.",
            "from collections import deque\ndef bfs(grid, start, end):\n    q = deque([(start, 0)])\n    visited = set()\n    while q:\n        (r, c), dist = q.popleft()\n        if (r, c) == end:\n            return dist\n        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:\n            nr, nc = r+dr, c+dc\n            if 0<=nr<len(grid) and 0<=nc<len(grid[0]):\n                visited.add((nr, nc))\n                q.append(((nr, nc), dist+1))\n    return -1",
            "python", "Shortest path length",
            ["Are we checking visited before adding?", "Could we visit the same cell twice?"],
            "Bug: Missing visited check before adding to queue, and start is never added to visited. Fix: add `if (nr,nc) not in visited:` before the append, and add start to visited initially."),

        # ─── TREES ───
        AdvancedQuestion(110, "Trees", "Medium", "snippet",
            "What traversal order does this produce for a BST? What is the significance?",
            "def traverse(root):\n    if root is None:\n        return []\n    return traverse(root.left) + [root.val] + traverse(root.right)",
            "python", "In-order traversal (sorted order for BST)",
            ["Left, Root, Right"],
            "This is in-order traversal (Left-Root-Right). For a BST, in-order traversal always produces elements in sorted ascending order. Time: O(n), Space: O(h) for recursion stack."),

        AdvancedQuestion(111, "Trees", "Hard", "debug",
            "This should find the height of a binary tree. Fix the bug.",
            "def height(root):\n    if root is None:\n        return 0\n    left = height(root.left)\n    right = height(root.right)\n    return left + right  # BUG",
            "python", "Height of the tree",
            ["Height = longest path from root to leaf", "Should we add both subtrees?"],
            "Bug: Returns sum of left and right heights instead of the maximum. Fix: `return max(left, right) + 1`. Height is the longest path, not the sum of all paths."),

        # ─── GRAPHS ───
        AdvancedQuestion(112, "Graphs", "Medium", "snippet",
            "What does this function compute? What is its time complexity?",
            "def dfs(graph, node, visited=None):\n    if visited is None:\n        visited = set()\n    visited.add(node)\n    for neighbor in graph[node]:\n        if neighbor not in visited:\n            dfs(graph, neighbor, visited)\n    return visited",
            "python", "All reachable nodes from a starting node",
            ["DFS explores all connected nodes"],
            "This performs DFS to find all nodes reachable from 'node'. Time: O(V+E) where V=vertices, E=edges. It returns the set of all visited nodes in the connected component."),

        # ─── RECURSION ───
        AdvancedQuestion(113, "Recursion", "Easy", "snippet",
            "What does this return for n=5? What is the time complexity?",
            "def f(n):\n    if n <= 1:\n        return n\n    return f(n-1) + f(n-2)",
            "python", "5 (Fibonacci)",
            ["Classic recursive pattern"],
            "This computes the nth Fibonacci number. f(5) = f(4)+f(3) = 3+2 = 5. Time complexity is O(2^n) due to overlapping subproblems. Can be optimized with memoization to O(n)."),

        AdvancedQuestion(114, "Recursion", "Medium", "debug",
            "This should compute power(base, exp). Fix the bug.",
            "def power(base, exp):\n    if exp == 0:\n        return 1\n    return base * power(base, exp)  # BUG",
            "python", "base^exp",
            ["Will this ever terminate?", "exp should decrease"],
            "Bug: Infinite recursion because exp never decreases. Fix: `return base * power(base, exp - 1)`. The recursive call must reduce the problem size."),

        # ─── DYNAMIC PROGRAMMING ───
        AdvancedQuestion(115, "Dynamic Programming", "Medium", "snippet",
            "What problem does this solve? Explain the DP table.",
            "def solve(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for coin in coins:\n        for x in range(coin, amount + 1):\n            dp[x] = min(dp[x], dp[x - coin] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1",
            "python", "Minimum number of coins to make the amount",
            ["dp[x] represents minimum coins for amount x"],
            "This solves the Coin Change problem using bottom-up DP. dp[x] = minimum coins needed to make amount x. For each coin, we check if using it gives a better solution. Time: O(amount * len(coins))."),

        AdvancedQuestion(116, "Dynamic Programming", "Hard", "debug",
            "This 0/1 knapsack has a bug. Find and fix it.",
            "def knapsack(W, weights, values, n):\n    dp = [[0]*(W+1) for _ in range(n+1)]\n    for i in range(1, n+1):\n        for w in range(1, W+1):\n            if weights[i-1] <= w:\n                dp[i][w] = values[i-1] + dp[i][w-weights[i-1]]  # BUG\n            else:\n                dp[i][w] = dp[i-1][w]\n    return dp[n][W]",
            "python", "Maximum value in knapsack",
            ["0/1 means each item used at most once", "Which row should we reference?"],
            "Bug: `dp[i][w-weights[i-1]]` allows reusing item i (unbounded). For 0/1 knapsack, it should be `dp[i-1][w-weights[i-1]]` to reference the previous row, ensuring each item is used at most once."),

        # ─── JAVA QUESTIONS ───
        AdvancedQuestion(117, "Arrays", "Easy", "snippet",
            "What does this Java code print?",
            "int[] arr = {1, 2, 3, 4, 5};\nint sum = 0;\nfor (int i = 0; i < arr.length; i += 2) {\n    sum += arr[i];\n}\nSystem.out.println(sum);",
            "java", "9",
            ["i increments by 2, so it hits indices 0, 2, 4"],
            "It prints 9. The loop visits indices 0, 2, 4, summing arr[0]+arr[2]+arr[4] = 1+3+5 = 9."),

        AdvancedQuestion(118, "Strings", "Medium", "debug",
            "This Java method should check if two strings are anagrams. Fix the bug.",
            "boolean isAnagram(String s, String t) {\n    if (s.length() != t.length()) return false;\n    int[] count = new int[26];\n    for (char c : s.toCharArray()) count[c - 'a']++;\n    for (char c : t.toCharArray()) count[c - 'a']++; // BUG\n    for (int i : count) if (i != 0) return false;\n    return true;\n}",
            "java", "true if anagrams",
            ["Should the second loop increment or decrement?"],
            "Bug: Second loop increments instead of decrementing. Fix: change `count[c-'a']++` to `count[c-'a']--` in the second loop. Anagram check requires one loop to add and one to subtract."),

        # ─── C++ QUESTIONS ───
        AdvancedQuestion(119, "Stacks", "Medium", "snippet",
            "What does this C++ code output?",
            "#include <stack>\nusing namespace std;\nstack<int> s;\ns.push(1); s.push(2); s.push(3);\nwhile (!s.empty()) {\n    cout << s.top() << \" \";\n    s.pop();\n}",
            "cpp", "3 2 1",
            ["Stack is LIFO"],
            "Output: 3 2 1. Stack follows LIFO (Last In First Out). Elements are pushed in order 1,2,3 but popped in reverse order 3,2,1."),

        AdvancedQuestion(120, "Dynamic Programming", "Hard", "debug",
            "This C++ Longest Common Subsequence has a bug. Fix it.",
            "int lcs(string a, string b) {\n    int m = a.size(), n = b.size();\n    vector<vector<int>> dp(m+1, vector<int>(n+1, 0));\n    for (int i = 1; i <= m; i++) {\n        for (int j = 1; j <= n; j++) {\n            if (a[i] == b[j])  // BUG\n                dp[i][j] = dp[i-1][j-1] + 1;\n            else\n                dp[i][j] = max(dp[i-1][j], dp[i][j-1]);\n        }\n    }\n    return dp[m][n];\n}",
            "cpp", "Length of LCS",
            ["Strings are 0-indexed but dp is 1-indexed"],
            "Bug: a[i] and b[j] should be a[i-1] and b[j-1] because the dp table is 1-indexed but string indexing is 0-based. a[m] would be out of bounds."),
    ]


def get_full_advanced_bank() -> List[AdvancedQuestion]:
    """Return the built-in bank PLUS all JSON snippet questions."""
    from .snippet_loader import load_snippet_questions
    return get_advanced_bank() + load_snippet_questions()


def get_snippet_bank(language: Optional[str] = None) -> List[AdvancedQuestion]:
    """Return ONLY the JSON snippet questions, optionally filtered by language."""
    from .snippet_loader import load_snippet_questions
    bank = load_snippet_questions()
    if language:
        bank = [q for q in bank if q.language.lower() == language.lower()]
    return bank


def get_advanced_questions(count: int = 8) -> List[AdvancedQuestion]:
    bank = get_full_advanced_bank()
    return random.sample(bank, min(count, len(bank)))


def get_advanced_topics() -> List[str]:
    return sorted({q.topic for q in get_full_advanced_bank()})
