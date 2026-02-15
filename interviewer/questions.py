from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Question:
    qid: int
    topic: str
    prompt: str
    expected_keywords: List[str]


def get_question_bank() -> List[Question]:
    return [
        Question(1, "DSA", "Explain the time and space complexity of binary search and when it works.", ["sorted", "log", "divide", "middle", "o(log n)"]),
        Question(2, "DSA", "How does a hash table handle collisions?", ["collision", "chaining", "open addressing", "rehashing"]),
        Question(3, "DSA", "What is the difference between BFS and DFS, and where would you use each?", ["queue", "stack", "shortest path", "traversal", "graph"]),
        Question(4, "DSA", "Describe merge sort and its complexity.", ["divide and conquer", "merge", "o(n log n)", "stable"]),
        Question(5, "DSA", "When would you choose a heap over a balanced BST?", ["priority queue", "top k", "insert", "extract min", "extract max"]),
        Question(6, "DSA", "What is dynamic programming? Explain overlapping subproblems and optimal substructure.", ["memoization", "tabulation", "overlapping", "optimal substructure"]),
        Question(7, "DSA", "Explain two-pointer technique with an example problem.", ["left", "right", "sorted", "linear", "window"]),
        Question(8, "DSA", "How would you detect a cycle in a linked list?", ["fast", "slow", "floyd", "tortoise", "hare"]),
        Question(9, "CN", "What is the TCP three-way handshake?", ["syn", "ack", "sequence", "connection establishment"]),
        Question(10, "CN", "Differentiate TCP and UDP with practical use cases.", ["reliable", "connectionless", "latency", "streaming", "ordering"]),
        Question(11, "CN", "What happens when you type a URL in a browser?", ["dns", "tcp", "tls", "http", "request", "response"]),
        Question(12, "CN", "Explain subnetting and why it is useful.", ["ip", "network", "host", "mask", "cidr"]),
        Question(13, "CN", "What are HTTP status code categories?", ["1xx", "2xx", "3xx", "4xx", "5xx"]),
        Question(14, "CN", "How does DNS resolution work at a high level?", ["resolver", "root", "tld", "authoritative", "cache"]),
        Question(15, "OS", "What is a process vs a thread?", ["address space", "lightweight", "context switch", "shared memory"]),
        Question(16, "OS", "Explain deadlock and the four Coffman conditions.", ["mutual exclusion", "hold and wait", "no preemption", "circular wait"]),
        Question(17, "OS", "How does virtual memory work?", ["paging", "page table", "swap", "frame"]),
        Question(18, "OS", "What is context switching and why is it expensive?", ["cpu", "register", "scheduler", "overhead"]),
        Question(19, "OS", "Explain producer-consumer problem and one synchronization solution.", ["semaphore", "mutex", "buffer", "critical section"]),
        Question(20, "OS", "Compare FCFS, SJF, and Round Robin scheduling.", ["waiting time", "turnaround", "quantum", "preemptive"]),
        Question(21, "Behavioral", "Tell me about yourself and your recent project impact.", ["role", "impact", "result", "team"]),
        Question(22, "Behavioral", "Describe a challenging bug you fixed. How did you approach it?", ["situation", "analysis", "action", "result"]),
        Question(23, "Behavioral", "Tell me about a time you handled conflict in a team.", ["communication", "empathy", "resolution", "outcome"]),
        Question(24, "Behavioral", "Describe a failure and what you learned from it.", ["ownership", "learning", "improvement", "result"]),
        Question(25, "Behavioral", "Why should we hire you for this role?", ["strength", "fit", "value", "impact"]),
        Question(26, "DSA", "How does quicksort work, and what are its best and worst-case complexities?", ["pivot", "partition", "o(n log n)", "o(n^2)"]),
        Question(27, "DSA", "Explain the difference between an array and a linked list.", ["contiguous", "pointer", "insertion", "access"]),
        Question(28, "DSA", "How would you find the kth largest element efficiently?", ["heap", "quickselect", "partition", "top k"]),
        Question(29, "DSA", "What is a monotonic stack and where is it used?", ["next greater", "increasing", "decreasing", "linear"]),
        Question(30, "DSA", "Explain sliding window technique with a substring problem example.", ["window", "expand", "shrink", "two pointers"]),
        Question(31, "CN", "What is TLS and why is it used over plain HTTP?", ["encryption", "certificate", "handshake", "https"]),
        Question(32, "CN", "Explain the purpose of NAT in networks.", ["private ip", "public ip", "translation", "router"]),
        Question(33, "CN", "What is the difference between hub, switch, and router?", ["broadcast", "mac", "ip", "forwarding"]),
        Question(34, "CN", "How does congestion control work in TCP?", ["window", "slow start", "avoidance", "packet loss"]),
        Question(35, "CN", "What is CDN and how does it improve web performance?", ["edge", "latency", "cache", "distributed"]),
        Question(36, "OS", "What is the role of system calls in an operating system?", ["kernel", "user mode", "interface", "privileged"]),
        Question(37, "OS", "Explain paging vs segmentation.", ["page", "segment", "address translation", "fragmentation"]),
        Question(38, "OS", "What is starvation and how is it different from deadlock?", ["priority", "indefinite waiting", "scheduling", "progress"]),
        Question(39, "OS", "How do mutex and semaphore differ?", ["locking", "counting", "critical section", "synchronization"]),
        Question(40, "OS", "What is thrashing in memory management?", ["page fault", "working set", "swap", "performance"]),
        Question(41, "Behavioral", "Tell me about a time you took ownership without being asked.", ["ownership", "initiative", "impact", "result"]),
        Question(42, "Behavioral", "Describe a situation where requirements changed late. What did you do?", ["adapt", "communication", "prioritize", "delivery"]),
        Question(43, "Behavioral", "How do you handle tight deadlines and stress?", ["planning", "prioritization", "communication", "focus"]),
        Question(44, "Behavioral", "Give an example of mentoring or helping a teammate grow.", ["mentoring", "support", "feedback", "outcome"]),
        Question(45, "Behavioral", "Describe a decision you made with incomplete information.", ["tradeoff", "assumption", "risk", "result"]),
    ]


def get_question_topics() -> List[str]:
    return sorted({question.topic for question in get_question_bank()})
