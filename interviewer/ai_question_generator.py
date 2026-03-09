"""
AI-powered question generator for debugging and coding rounds.
Uses Gemini API to dynamically create interview questions.
Falls back to static question bank if API is unavailable.
"""
from __future__ import annotations

import json
import logging
import random
from typing import Dict, List, Optional

from .ai_service import _call_gemini
from .prompts import (
    GENERATE_DEBUG_QUESTION_SYSTEM,
    GENERATE_DEBUG_QUESTION_USER,
    GENERATE_CODING_QUESTION_SYSTEM,
    GENERATE_CODING_QUESTION_USER,
    GENERATE_LOGICAL_QUESTION_SYSTEM,
    GENERATE_LOGICAL_QUESTION_USER,
    DSA_TOPICS,
    LOGICAL_TOPICS,
    DSA_DIFFICULTIES,
    DIFFICULTY_WEIGHTS,
)

logger = logging.getLogger(__name__)


def _pick_topic(used_topics: List[str]) -> str:
    """Pick a topic that hasn't been used recently."""
    available = [t for t in DSA_TOPICS if t not in used_topics]
    if not available:
        available = DSA_TOPICS
    return random.choice(available)


def _pick_logical_topic(used_topics: List[str]) -> str:
    """Pick a logical topic that hasn't been used recently."""
    available = [t for t in LOGICAL_TOPICS if t not in used_topics]
    if not available:
        available = LOGICAL_TOPICS
    return random.choice(available)


def _pick_difficulty(question_number: int, total: int) -> str:
    """Gradually increase difficulty as the interview progresses."""
    progress = question_number / max(total, 1)
    if progress < 0.3:
        weights = [0.50, 0.40, 0.10]
    elif progress < 0.7:
        weights = [0.20, 0.50, 0.30]
    else:
        weights = [0.10, 0.40, 0.50]
    return random.choices(DSA_DIFFICULTIES, weights=weights, k=1)[0]


def generate_debug_question(
    language: str,
    used_topics: List[str],
    question_number: int = 1,
    total_questions: int = 5,
) -> Optional[Dict]:
    """
    Generate a debugging question using AI.
    Returns a dict with topic, title, difficulty, description, buggy_code, etc.
    """
    difficulty = _pick_difficulty(question_number, total_questions)
    topic = _pick_topic(used_topics)

    user_prompt = GENERATE_DEBUG_QUESTION_USER.format(
        difficulty=difficulty,
        language=language,
        topic=topic,
        used_topics=", ".join(used_topics[-5:]) if used_topics else "none",
    )

    raw = _call_gemini(
        GENERATE_DEBUG_QUESTION_SYSTEM,
        user_prompt,
        max_tokens=1024,
        temperature=0.8,
    )

    if not raw:
        logger.warning("AI question generation failed, using fallback")
        return None

    try:
        text = raw.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        # Validate required fields
        required = ["topic", "title", "difficulty", "description", "buggy_code"]
        if not all(data.get(k) for k in required):
            logger.warning("AI response missing required fields: %s", data.keys())
            return None

        return {
            "type": "debug",
            "topic": str(data["topic"]),
            "title": str(data["title"]),
            "difficulty": str(data.get("difficulty", difficulty)),
            "description": str(data["description"]),
            "buggy_code": str(data["buggy_code"]),
            "bug_explanation": str(data.get("bug_explanation", "")),
            "fixed_code": str(data.get("fixed_code", "")),
            "hints": list(data.get("hints", [])),
            "test_cases": list(data.get("test_cases", [])),
            "language": language,
        }
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Failed to parse AI debug question: %s", exc)
        return None


def generate_coding_question(
    language: str,
    used_topics: List[str],
    question_number: int = 1,
    total_questions: int = 5,
) -> Optional[Dict]:
    """
    Generate a coding challenge using AI.
    Returns a dict with topic, title, description, starter_code, solution, test_cases, etc.
    """
    difficulty = _pick_difficulty(question_number, total_questions)
    topic = _pick_topic(used_topics)

    user_prompt = GENERATE_CODING_QUESTION_USER.format(
        difficulty=difficulty,
        language=language,
        topic=topic,
        used_topics=", ".join(used_topics[-5:]) if used_topics else "none",
    )

    raw = _call_gemini(
        GENERATE_CODING_QUESTION_SYSTEM,
        user_prompt,
        max_tokens=1500,
        temperature=0.8,
    )

    if not raw:
        logger.warning("AI coding question generation failed, using fallback")
        return None

    try:
        text = raw.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        required = ["topic", "title", "description", "starter_code"]
        if not all(data.get(k) for k in required):
            logger.warning("AI coding response missing fields: %s", data.keys())
            return None

        return {
            "type": "coding",
            "topic": str(data["topic"]),
            "title": str(data["title"]),
            "difficulty": str(data.get("difficulty", difficulty)),
            "description": str(data["description"]),
            "examples": list(data.get("examples", [])),
            "constraints": list(data.get("constraints", [])),
            "starter_code": str(data["starter_code"]),
            "solution_code": str(data.get("solution_code", "")),
            "test_cases": list(data.get("test_cases", [])),
            "time_complexity": str(data.get("time_complexity", "")),
            "space_complexity": str(data.get("space_complexity", "")),
            "language": language,
        }
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Failed to parse AI coding question: %s", exc)
        return None


def generate_logical_question(
    used_topics: List[str],
    question_number: int = 1,
    total_questions: int = 5,
) -> Optional[Dict]:
    """
    Generate a logical/reasoning question using AI.
    Returns a dict with topic, title, description, correct_answer.
    """
    difficulty = _pick_difficulty(question_number, total_questions)
    topic = _pick_logical_topic(used_topics)

    user_prompt = GENERATE_LOGICAL_QUESTION_USER.format(
        difficulty=difficulty,
        topic=topic,
        used_topics=", ".join(used_topics[-5:]) if used_topics else "none",
    )

    raw = _call_gemini(
        GENERATE_LOGICAL_QUESTION_SYSTEM,
        user_prompt,
        max_tokens=1000,
        temperature=0.8,
    )

    if not raw:
        logger.warning("AI logical question generation failed, using fallback")
        return None

    try:
        text = raw.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        required = ["topic", "title", "description", "correct_answer"]
        if not all(data.get(k) for k in required):
            logger.warning("AI logical response missing fields: %s", data.keys())
            return None

        return {
            "type": "logical",
            "topic": str(data["topic"]),
            "title": str(data["title"]),
            "difficulty": str(data.get("difficulty", difficulty)),
            "description": str(data["description"]),
            "hints": list(data.get("hints", [])),
            "correct_answer": str(data["correct_answer"]),
        }
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Failed to parse AI logical question: %s", exc)
        return None

# ═══════════════════════════════════════════════
#  FALLBACK QUESTIONS (when AI is unavailable)
# ═══════════════════════════════════════════════

_FALLBACK_DEBUG = {
    "python": [
        {
            "type": "debug", "topic": "Arrays", "title": "Two Sum Bug",
            "difficulty": "Easy", "language": "python",
            "description": "This function should return indices of two numbers that sum to target. Find and fix the bug.",
            "buggy_code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        comp = target - num\n        if comp in seen:\n            return [i, seen[comp]]  # Bug: indices are swapped\n        seen[num] = i\n    return []",
            "bug_explanation": "The return statement has indices in wrong order. Should be [seen[comp], i].",
            "fixed_code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        comp = target - num\n        if comp in seen:\n            return [seen[comp], i]\n        seen[num] = i\n    return []",
            "hints": ["Check the order of returned indices", "The earlier index should come first"],
            "test_cases": [{"input": "nums=[2,7,11,15], target=9", "expected": "[0, 1]"}],
        },
        {
            "type": "debug", "topic": "Binary Search", "title": "Binary Search Off-by-One",
            "difficulty": "Medium", "language": "python",
            "description": "This binary search should return the index of target in a sorted array. Find and fix the bug.",
            "buggy_code": "def binary_search(arr, target):\n    lo, hi = 0, len(arr)\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
            "bug_explanation": "hi should be initialized to len(arr) - 1, not len(arr). This causes an IndexError.",
            "fixed_code": "def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
            "hints": ["Check the initial value of hi", "What happens when mid equals len(arr)?"],
            "test_cases": [{"input": "arr=[1,3,5,7,9], target=5", "expected": "2"}],
        },
        {
            "type": "debug", "topic": "Linked Lists", "title": "Reverse Linked List Bug",
            "difficulty": "Medium", "language": "python",
            "description": "This function should reverse a singly linked list in-place. Find and fix the bug.",
            "buggy_code": "def reverse_list(head):\n    prev = None\n    curr = head\n    while curr:\n        next_node = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_node\n    return curr  # Bug: should return prev",
            "bug_explanation": "Returns curr (which is None after the loop) instead of prev (the new head).",
            "fixed_code": "def reverse_list(head):\n    prev = None\n    curr = head\n    while curr:\n        next_node = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_node\n    return prev",
            "hints": ["What is the value of curr after the loop ends?", "Which variable holds the new head?"],
            "test_cases": [{"input": "1->2->3->4->5", "expected": "5->4->3->2->1"}],
        },
        {
            "type": "debug", "topic": "Dynamic Programming", "title": "Fibonacci Memoization Bug",
            "difficulty": "Easy", "language": "python",
            "description": "This memoized Fibonacci should be O(n). Find and fix the bug.",
            "buggy_code": "def fib(n, memo={}):\n    if n <= 1:\n        return n\n    if n in memo:\n        return memo[n]\n    result = fib(n - 1) + fib(n - 2)  # Bug: not passing memo\n    memo[n] = result\n    return result",
            "bug_explanation": "Recursive calls don't pass memo dict, so memoization doesn't work properly across calls.",
            "fixed_code": "def fib(n, memo={}):\n    if n <= 1:\n        return n\n    if n in memo:\n        return memo[n]\n    result = fib(n - 1, memo) + fib(n - 2, memo)\n    memo[n] = result\n    return result",
            "hints": ["Are the recursive calls using the cache?", "Check what parameters are passed"],
            "test_cases": [{"input": "n=10", "expected": "55"}],
        },
        {
            "type": "debug", "topic": "Trees", "title": "Max Depth Calculation Bug",
            "difficulty": "Easy", "language": "python",
            "description": "This function should return the maximum depth of a binary tree. Find and fix the bug.",
            "buggy_code": "def max_depth(root):\n    if root is None:\n        return 0\n    left = max_depth(root.left)\n    right = max_depth(root.right)\n    return left + right  # Bug: should be max + 1",
            "bug_explanation": "Returns sum of depths instead of max depth + 1. Depth = max(left, right) + 1.",
            "fixed_code": "def max_depth(root):\n    if root is None:\n        return 0\n    left = max_depth(root.left)\n    right = max_depth(root.right)\n    return max(left, right) + 1",
            "hints": ["Depth is about the longest path, not sum", "You need max(), not addition"],
            "test_cases": [{"input": "tree=[3,9,20,null,null,15,7]", "expected": "3"}],
        },
    ],
    "java": [
        {
            "type": "debug", "topic": "Arrays", "title": "Array Rotation Bug",
            "difficulty": "Medium", "language": "java",
            "description": "This function should rotate an array right by k positions. Find and fix the bug.",
            "buggy_code": "void rotate(int[] nums, int k) {\n    int n = nums.length;\n    k = k % n;\n    reverse(nums, 0, n);\n    reverse(nums, 0, k - 1);\n    reverse(nums, k, n - 1);\n}\nvoid reverse(int[] nums, int l, int r) {\n    while (l < r) {\n        int tmp = nums[l];\n        nums[l] = nums[r];\n        nums[r] = tmp;\n        l++; r--;\n    }\n}",
            "bug_explanation": "First reverse call uses n instead of n-1. Should be reverse(nums, 0, n-1).",
            "fixed_code": "void rotate(int[] nums, int k) {\n    int n = nums.length;\n    k = k % n;\n    reverse(nums, 0, n - 1);\n    reverse(nums, 0, k - 1);\n    reverse(nums, k, n - 1);\n}\nvoid reverse(int[] nums, int l, int r) {\n    while (l < r) {\n        int tmp = nums[l];\n        nums[l] = nums[r];\n        nums[r] = tmp;\n        l++; r--;\n    }\n}",
            "hints": ["Check the bounds in the first reverse call", "Array indices go from 0 to n-1"],
            "test_cases": [{"input": "[1,2,3,4,5,6,7], k=3", "expected": "[5,6,7,1,2,3,4]"}],
        },
    ],
    "cpp": [
        {
            "type": "debug", "topic": "Stacks", "title": "Valid Parentheses Bug",
            "difficulty": "Easy", "language": "cpp",
            "description": "This function should check if parentheses are balanced. Find and fix the bug.",
            "buggy_code": "#include <stack>\nbool isValid(string s) {\n    stack<char> st;\n    for (char c : s) {\n        if (c == '(' || c == '{' || c == '[')\n            st.push(c);\n        else {\n            if (st.empty()) return false;\n            char top = st.top();\n            if ((c == ')' && top != '(') ||\n                (c == '}' && top != '{') ||\n                (c == ']' && top != '['))\n                return false;\n        }\n    }\n    return true;  // Bug: should check if stack is empty\n}",
            "bug_explanation": "Missing st.pop() after checking top, and should return st.empty() not true.",
            "fixed_code": "#include <stack>\nbool isValid(string s) {\n    stack<char> st;\n    for (char c : s) {\n        if (c == '(' || c == '{' || c == '[')\n            st.push(c);\n        else {\n            if (st.empty()) return false;\n            char top = st.top();\n            st.pop();\n            if ((c == ')' && top != '(') ||\n                (c == '}' && top != '{') ||\n                (c == ']' && top != '['))\n                return false;\n        }\n    }\n    return st.empty();\n}",
            "hints": ["Are you removing matched brackets from the stack?", "What if there are unmatched opening brackets?"],
            "test_cases": [{"input": "\"()[]{}\"", "expected": "true"}],
        },
    ],
}

_FALLBACK_CODING = {
    "python": [
        {
            "type": "coding", "topic": "Arrays", "title": "Maximum Subarray Sum",
            "difficulty": "Medium", "language": "python",
            "description": "Given an integer array nums, find the contiguous subarray with the largest sum and return its sum. Use Kadane's algorithm for O(n) time.",
            "examples": [
                {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "Subarray [4,-1,2,1] has sum 6"},
                {"input": "nums = [1]", "output": "1", "explanation": "Single element"},
            ],
            "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
            "starter_code": "def max_subarray(nums):\n    # TODO: Implement Kadane's algorithm\n    # Return the maximum subarray sum\n    pass",
            "solution_code": "def max_subarray(nums):\n    max_sum = cur_sum = nums[0]\n    for num in nums[1:]:\n        cur_sum = max(num, cur_sum + num)\n        max_sum = max(max_sum, cur_sum)\n    return max_sum",
            "test_cases": [
                {"input": "[-2,1,-3,4,-1,2,1,-5,4]", "expected": "6"},
                {"input": "[1]", "expected": "1"},
                {"input": "[-1]", "expected": "-1"},
            ],
            "time_complexity": "O(n)", "space_complexity": "O(1)",
        },
        {
            "type": "coding", "topic": "Two Pointers", "title": "Container With Most Water",
            "difficulty": "Medium", "language": "python",
            "description": "Given n non-negative integers representing heights, find two lines that form a container holding the most water. Return the maximum amount of water.",
            "examples": [
                {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49", "explanation": "Lines at index 1 and 8"},
            ],
            "constraints": ["2 <= n <= 10^5", "0 <= height[i] <= 10^4"],
            "starter_code": "def max_area(height):\n    # TODO: Use two pointers approach\n    # Return maximum water area\n    pass",
            "solution_code": "def max_area(height):\n    l, r = 0, len(height) - 1\n    best = 0\n    while l < r:\n        area = min(height[l], height[r]) * (r - l)\n        best = max(best, area)\n        if height[l] < height[r]:\n            l += 1\n        else:\n            r -= 1\n    return best",
            "test_cases": [
                {"input": "[1,8,6,2,5,4,8,3,7]", "expected": "49"},
                {"input": "[1,1]", "expected": "1"},
            ],
            "time_complexity": "O(n)", "space_complexity": "O(1)",
        },
        {
            "type": "coding", "topic": "Hash Tables", "title": "Group Anagrams",
            "difficulty": "Medium", "language": "python",
            "description": "Given an array of strings, group the anagrams together. Return the groups in any order. Two strings are anagrams if they contain the same characters in different order.",
            "examples": [
                {"input": 'strs = ["eat","tea","tan","ate","nat","bat"]', "output": '[["bat"],["nat","tan"],["ate","eat","tea"]]', "explanation": "Grouped by sorted character key"},
            ],
            "constraints": ["1 <= strs.length <= 10^4", "0 <= strs[i].length <= 100"],
            "starter_code": "def group_anagrams(strs):\n    # TODO: Group strings that are anagrams\n    # Return list of groups\n    pass",
            "solution_code": "from collections import defaultdict\ndef group_anagrams(strs):\n    groups = defaultdict(list)\n    for s in strs:\n        key = ''.join(sorted(s))\n        groups[key].append(s)\n    return list(groups.values())",
            "test_cases": [
                {"input": '["eat","tea","tan","ate","nat","bat"]', "expected": '3 groups'},
                {"input": '[""]', "expected": '1 group'},
                {"input": '["a"]', "expected": '1 group'},
            ],
            "time_complexity": "O(n * k log k)", "space_complexity": "O(n * k)",
        },
        {
            "type": "coding", "topic": "Sliding Window", "title": "Longest Substring Without Repeating",
            "difficulty": "Medium", "language": "python",
            "description": "Given a string s, find the length of the longest substring without repeating characters.",
            "examples": [
                {"input": "s = 'abcabcbb'", "output": "3", "explanation": "'abc' is the longest"},
                {"input": "s = 'bbbbb'", "output": "1", "explanation": "'b' is the longest"},
            ],
            "constraints": ["0 <= s.length <= 5 * 10^4"],
            "starter_code": "def length_of_longest_substring(s):\n    # TODO: Use sliding window\n    # Return length of longest substring without repeating chars\n    pass",
            "solution_code": "def length_of_longest_substring(s):\n    seen = {}\n    left = best = 0\n    for right, ch in enumerate(s):\n        if ch in seen and seen[ch] >= left:\n            left = seen[ch] + 1\n        seen[ch] = right\n        best = max(best, right - left + 1)\n    return best",
            "test_cases": [
                {"input": "'abcabcbb'", "expected": "3"},
                {"input": "'bbbbb'", "expected": "1"},
                {"input": "''", "expected": "0"},
            ],
            "time_complexity": "O(n)", "space_complexity": "O(min(n, m))",
        },
        {
            "type": "coding", "topic": "Graphs", "title": "Number of Islands",
            "difficulty": "Medium", "language": "python",
            "description": "Given an m x n 2D grid of '1's (land) and '0's (water), count the number of islands. An island is surrounded by water and formed by connecting adjacent lands horizontally or vertically.",
            "examples": [
                {"input": "grid = [[1,1,0,0,0],[1,1,0,0,0],[0,0,1,0,0],[0,0,0,1,1]]", "output": "3", "explanation": "Three separate island groups"},
            ],
            "constraints": ["1 <= m, n <= 300", "grid[i][j] is '0' or '1'"],
            "starter_code": "def num_islands(grid):\n    # TODO: Count connected components of 1s\n    # Use DFS or BFS\n    pass",
            "solution_code": "def num_islands(grid):\n    if not grid:\n        return 0\n    rows, cols = len(grid), len(grid[0])\n    count = 0\n    def dfs(r, c):\n        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':\n            return\n        grid[r][c] = '0'\n        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1':\n                count += 1\n                dfs(r, c)\n    return count",
            "test_cases": [
                {"input": "[[1,1,0],[0,1,0],[0,0,1]]", "expected": "2"},
                {"input": "[[1]]", "expected": "1"},
                {"input": "[[0]]", "expected": "0"},
            ],
            "time_complexity": "O(m*n)", "space_complexity": "O(m*n)",
        },
    ],
}


_FALLBACK_LOGICAL = [
    {
        "type": "logical", "topic": "Math Puzzles", "title": "Lily Pad Puzzle",
        "difficulty": "Easy",
        "description": "A lily pad in a pond doubles in size every day. It takes 30 days to cover the entire pond. How long does it take to cover half the pond?",
        "correct_answer": "29 days. Since it doubles every day, it must have been half the size the day before it covered the whole pond.",
        "hints": ["Work backwards from day 30.", "If it's full on day 30 and doubles each day, what was it on day 29?"],
    },
    {
        "type": "logical", "topic": "Probability", "title": "Three Doors (Monty Hall)",
        "difficulty": "Medium",
        "description": "You are on a game show with 3 doors. Behind one is a car; behind the others, goats. You pick a door (say, Door 1). The host, who knows what's behind the doors, opens another door (say, Door 3) to reveal a goat. He then offers you the chance to switch your choice to Door 2. Should you switch? Why?",
        "correct_answer": "Yes, you should switch. Initially, you have a 1/3 chance of picking the car and a 2/3 chance of picking a goat. If you picked a goat, switching guarantees you the car. Thus, switching gives you a 2/3 chance of winning.",
        "hints": ["What is the probability you picked the car correctly on your first guess?", "If there is only a 1/3 chance you were right, there is a 2/3 chance the car is behind one of the other doors."],
    },
    {
        "type": "logical", "topic": "Brainteasers", "title": "Two Ropes",
        "difficulty": "Hard",
        "description": "You have two ropes. Each rope takes exactly 60 minutes to burn completely, but they do NOT burn at a uniform rate (e.g., half the rope might burn in 10 mins and the rest in 50 mins). How can you measure exactly 45 minutes using only these two ropes and a lighter?",
        "correct_answer": "Light the first rope at both ends, and the second rope at one end. The first rope will burn out in exactly 30 minutes. At the moment it burns out, light the other end of the second rope. The second rope, which has 30 minutes left to burn, will now burn out in exactly 15 minutes. 30 + 15 = 45 minutes.",
        "hints": ["What happens if you light a 60 minute rope from both ends?", "When a rope lit at both ends finishes, how much time has passed?"],
    }
]


def get_fallback_debug(language: str, used_indices: List[int]) -> Optional[Dict]:
    """Return a fallback debug question for the given language."""
    bank = _FALLBACK_DEBUG.get(language, _FALLBACK_DEBUG["python"])
    available = [q for i, q in enumerate(bank) if i not in used_indices]
    if not available:
        available = bank
    return random.choice(available) if available else None


def get_fallback_coding(language: str, used_indices: List[int]) -> Optional[Dict]:
    """Return a fallback coding question for the given language."""
    bank = _FALLBACK_CODING.get(language, _FALLBACK_CODING["python"])
    available = [q for i, q in enumerate(bank) if i not in used_indices]
    if not available:
        available = bank
    return random.choice(available) if available else None


def get_fallback_logical(used_indices: List[int]) -> Optional[Dict]:
    """Return a fallback logical question."""
    bank = _FALLBACK_LOGICAL
    available = [q for i, q in enumerate(bank) if i not in used_indices]
    if not available:
        available = bank
    return random.choice(available) if available else None
