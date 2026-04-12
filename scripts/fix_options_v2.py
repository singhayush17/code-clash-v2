#!/usr/bin/env python3
"""
Second pass: for ALL questions where correct is obviously longest,
pad the wrong options with plausible-sounding technical detail to bring
them closer in length to the correct answer.

Strategy per wrong option:
  - If the option is very short (< 30 chars), append a plausible-sounding
    clarifying clause using category-appropriate templates.
  - Ensure the *wrong* options become roughly similar in length to correct.
"""

import json
import random
import os
import re

INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "questions.json")
OUTPUT = INPUT

with open(INPUT) as f:
    questions = json.load(f)

# Templates for expanding short wrong options based on category
EXPANSION_TEMPLATES = {
    "DSA": [
        "commonly used in competitive programming contexts",
        "applicable only to sorted data structures",
        "requiring O(n²) auxiliary space in most cases",
        "optimized for cache-friendly sequential access patterns",
        "useful in parallel processing of partitioned arrays",
        "designed for linked-list-based data storage only",
        "relying on comparison-based sorting as a substep",
        "implemented using recursion with memoization tables",
        "typically applied to graph traversal problems only",
        "based on greedy selection of locally optimal choices",
    ],
    "Java": [
        "introduced in Java 5 as part of the concurrency API",
        "enforced at compile-time by the Java type checker",
        "available only in commercial JVM distributions",
        "requiring explicit synchronization in all use cases",
        "applicable only when running in server JVM mode",
        "managed by the garbage collector during STW pauses",
        "used primarily for debugging and profiling purposes",
        "handled automatically by the classloader subsystem",
        "specified in the Java Language Specification chapter 17",
        "deprecated since Java 11 in favor of newer alternatives",
    ],
    "OOPS": [
        "commonly used in enterprise Java applications",
        "applicable only to statically typed class hierarchies",
        "requiring abstract base classes in all implementations",
        "used for managing object lifecycle and dependency wiring",
        "designed for reducing coupling between software modules",
        "involving polymorphic dispatch through virtual method tables",
        "applicable in distributed systems communication patterns",
        "based on composition over inheritance design principles",
        "requiring reflection to inspect object metadata at runtime",
        "optimized for testability with mock object injection patterns",
    ],
    "OS": [
        "managed by the kernel scheduler during context switches",
        "relevant only in real-time operating system environments",
        "applicable to both user-space and kernel-space operations",
        "requiring privileged ring-0 access to hardware resources",
        "implemented differently across POSIX and Windows kernels",
        "used in embedded systems with limited memory constraints",
        "handled by the memory management unit at the hardware level",
        "involving the interrupt descriptor table for event routing",
        "applicable to multi-core symmetric multiprocessing systems",
        "relying on virtual address translation via page table lookups",
    ],
    "CN": [
        "standardized by the IEEE 802 working group specifications",
        "operating at the transport layer of the OSI reference model",
        "applicable to both IPv4 and IPv6 network protocol stacks",
        "requiring specialized hardware support in network adapters",
        "used primarily in enterprise campus network deployments",
        "implemented in kernel-space network driver protocol stacks",
        "relying on TCP sequence numbers for reliable data delivery",
        "specified in the original ARPANET protocol design documents",
        "applicable to both wired and wireless network topologies",
        "involving packet fragmentation at the network layer boundary",
    ],
    "System Design": [
        "commonly deployed in cloud-native microservice architectures",
        "applicable only to strongly consistent storage backends",
        "requiring horizontal scaling across multiple availability zones",
        "used in real-time event-driven stream processing pipelines",
        "designed for high-throughput write-heavy workload patterns",
        "implemented using distributed consensus protocol algorithms",
        "applicable to both relational and NoSQL database storage systems",
        "requiring careful capacity planning for production deployments",
        "optimized for read-heavy workloads with eventual consistency",
        "involving service mesh sidecar proxies for traffic management",
    ],
    "Data Engineering": [
        "commonly used in cloud data warehouse query optimization",
        "applicable to both batch and streaming data pipeline workloads",
        "requiring distributed compute clusters for parallel processing",
        "used in data lake architectures with schema-on-read patterns",
        "designed for handling petabyte-scale analytical data processing",
        "implemented in Apache Spark using catalyst query optimizer",
        "applicable to columnar storage formats like Parquet and ORC",
        "requiring data governance policies for regulatory compliance",
        "optimized for reducing data shuffle across network partitions",
        "involving metadata management in centralized data catalog systems",
    ],
    "Aptitude": [
        "using basic arithmetic operations and number properties",
        "applicable to competitive exam quantitative reasoning",
        "based on fundamental algebraic equation manipulation",
        "derived from standard combinatorics counting principles",
        "using the ratio and proportion identity relationship",
        "applicable to percentage and fraction conversion problems",
        "based on time-speed-distance formula rearrangement",
        "derived from profit-loss margin calculation formulas",
        "using simple interest compound interest growth formulas",
        "applicable to probability and set theory union rules",
    ],
}

def avg_len(strings):
    return sum(len(s) for s in strings) / max(len(strings), 1)

def needs_fix(q):
    opts = q["options"]
    ci = q["answerIndex"]
    clen = len(opts[ci])
    wlens = [len(opts[i]) for i in range(len(opts)) if i != ci]
    max_w = max(wlens) if wlens else 0
    avg_w = avg_len([opts[i] for i in range(len(opts)) if i != ci])
    return clen > max_w and clen > avg_w * 1.35 and clen > 25

def expand_option(text, target_len, category):
    """Expand a short wrong option to be closer to target_len."""
    if len(text) >= target_len * 0.75:
        return text  # Already long enough
    
    templates = EXPANSION_TEMPLATES.get(category, EXPANSION_TEMPLATES["DSA"])
    
    # Pick a random expansion that isn't too similar to existing text
    random.shuffle(templates)
    for tmpl in templates:
        if any(word in text.lower() for word in tmpl.split()[:3]):
            continue
        
        # Clean up the text and append
        text_clean = text.rstrip(".")
        expanded = f"{text_clean}, {tmpl}"
        if len(expanded) >= target_len * 0.6:
            return expanded
    
    return text

def shorten_correct(text, target_len):
    """Try to shorten a correct answer while keeping it meaningful."""
    if len(text) <= target_len * 1.3:
        return text
    
    # Remove parenthetical details
    shortened = re.sub(r'\s*\([^)]{10,}\)', '', text)
    if len(shortened) > 20 and len(shortened) < len(text):
        text = shortened
    
    # Remove trailing clauses after em-dashes or semicolons if still too long
    if len(text) > target_len * 1.5:
        for sep in [' — ', ' – ', '; ']:
            parts = text.split(sep)
            if len(parts) > 1 and len(parts[0]) > 20:
                candidate = parts[0]
                if len(candidate) < len(text):
                    text = candidate
                    break
    
    return text

random.seed(42)
fixed = 0

for q in questions:
    if not needs_fix(q):
        continue
    
    opts = q["options"]
    ci = q["answerIndex"]
    cat = q["category"]
    clen = len(opts[ci])
    
    # First try to shorten the correct answer
    target = int(clen * 0.85)
    opts[ci] = shorten_correct(opts[ci], target)
    clen = len(opts[ci])
    
    # Then expand wrong options
    for i in range(len(opts)):
        if i == ci:
            continue
        opts[i] = expand_option(opts[i], clen, cat)
    
    q["options"] = opts
    fixed += 1

# Write back
with open(OUTPUT, "w") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

# Stats
total = 0
correct_longer = 0
for q in questions:
    opts = q["options"]
    ci = q["answerIndex"]
    clen = len(opts[ci])
    wlens = [len(opts[i]) for i in range(len(opts)) if i != ci]
    total += 1
    if clen > max(wlens):
        correct_longer += 1

avg_c = sum(len(q["options"][q["answerIndex"]]) for q in questions) / total
avg_w = sum(
    sum(len(q["options"][i]) for i in range(len(q["options"])) if i != q["answerIndex"])
    for q in questions
) / (total * 3)

print(f"Fixed: {fixed} questions")
print(f"Correct answer longest: {correct_longer}/{total} ({correct_longer*100//total}%)")
print(f"Avg correct len: {avg_c:.1f}")
print(f"Avg wrong len: {avg_w:.1f}")
