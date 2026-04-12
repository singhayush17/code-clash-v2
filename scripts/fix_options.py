#!/usr/bin/env python3
"""
Fix MCQ options so the correct answer isn't always the longest.
Strategy:
  1. If CORRECT is the longest AND significantly longer than wrong options,
     shorten the correct answer and/or expand the wrong answers.
  2. Keep all options plausible and roughly comparable in length.
"""

import json
import random
import os

INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "questions.json")
OUTPUT = INPUT  # overwrite in-place

with open(INPUT) as f:
    questions = json.load(f)

# ── helpers ──
def avg_len(strings):
    return sum(len(s) for s in strings) / max(len(strings), 1)


def needs_fix(q):
    """Return True if the correct option is obviously longest."""
    opts = q["options"]
    ci = q["answerIndex"]
    correct_len = len(opts[ci])
    wrong_lens = [len(opts[i]) for i in range(len(opts)) if i != ci]
    max_wrong = max(wrong_lens) if wrong_lens else 0
    avg_wrong = avg_len([opts[i] for i in range(len(opts)) if i != ci])
    # Flag if correct is >1.5x the average wrong length AND longer than all wrong
    return correct_len > max_wrong and correct_len > avg_wrong * 1.5 and correct_len > 30


# ── Detailed rewrite map ──
# For questions where the pattern is obvious, we rewrite options to be balanced.
# Each entry: question_id -> new options list (same answerIndex)

REWRITES = {
    # OOPS
    "oops-0231": {
        "options": [
            "A linked list structure for sequential data processing",
            "A TCP/IP connection chain for reliable data transfer",
            "A staged pipeline for sequential database queries",
            "A chain of handler objects where a request is passed along until one handles it"
        ],
        "answerIndex": 3
    },
    "oops-0198": {
        "options": [
            "Keywords that manage heap and stack memory allocation",
            "Keywords that control visibility of classes, methods, and fields",
            "Keywords that handle checked and unchecked exceptions",
            "Keywords that optimize code execution at compile time"
        ],
        "answerIndex": 1
    },
    "oops-0232": {
        "options": [
            "A set of database transaction guarantees for data integrity",
            "A suite of symmetric and asymmetric encryption standards",
            "Five OOP principles: SRP, Open/Closed, Liskov, ISP, and DIP",
            "A family of high-performance network protocols for microservices"
        ],
        "answerIndex": 2
    },
    "oops-0207": {
        "options": [
            "Delegating object creation to a factory method, decoupling clients from concrete classes",
            "A comparison-based pattern for sorting collections in-place",
            "A message routing pattern for distributed network topologies",
            "A DDL pattern for programmatic database table creation"
        ],
        "answerIndex": 0
    },
    "oops-0216": {
        "options": [
            "Prefer many specific interfaces over one fat interface clients don't fully use",
            "Interfaces should declare at most one abstract method each",
            "All interfaces must use public access modifiers exclusively",
            "Interfaces cannot extend or inherit from other interfaces"
        ],
        "answerIndex": 0
    },
    "oops-0225": {
        "options": [
            "A persistence pattern for creating database connections on demand",
            "A concurrency pattern for parallel object construction across threads",
            "A CI/CD pattern for incremental code compilation and linking",
            "A step-by-step construction pattern using named methods for readability"
        ],
        "answerIndex": 3
    },
    "oops-0235": {
        "options": [
            "A coding standard requiring methods to be under 10 lines of code",
            "A principle that objects should only talk to their immediate collaborators",
            "A memory optimization rule to minimize fields per object instance",
            "A design rule limiting classes to at most three member fields"
        ],
        "answerIndex": 1
    },
    "oops-0205": {
        "options": [
            "Existing methods should never be modified after initial deployment",
            "All classes should be declared final to prevent extension",
            "Interfaces must not include any default method implementations",
            "Entities should be open for extension but closed for modification"
        ],
        "answerIndex": 3
    },
    "oops-0201": {
        "options": [
            "Helper methods for executing parameterized database queries",
            "Utility methods for sorting and filtering collection data",
            "Error-handling methods for catching runtime exceptions gracefully",
            "Methods providing controlled read/write access to private fields"
        ],
        "answerIndex": 3
    },

    # Java
    "java-0303": {
        "options": [
            "Only null values are allowed but not null keys",
            "Only null keys are allowed but not null values",
            "Yes, both null keys and null values are allowed",
            "No, neither null keys nor null values are allowed"
        ],
        "answerIndex": 3
    },
    "java-0307": {
        "options": [
            "Storing descriptive thread names for debugging and logging",
            "Pinning a thread to a specific CPU core for performance",
            "Sharing a single variable instance safely across all threads",
            "Giving each thread its own independent copy of a variable"
        ],
        "answerIndex": 3
    },
    "java-0328": {
        "options": [
            "Determining if objects stay local to enable stack allocation or lock elimination",
            "A runtime security pattern for sandboxing untrusted code modules",
            "Analysis of exceptions escaping try blocks during stack unwinding",
            "Detection of memory leaks through object reference graph traversal"
        ],
        "answerIndex": 0
    },
    "java-0292": {
        "options": [
            "Checked must be caught or declared at compile-time; unchecked do not",
            "Checked exceptions run faster due to compiler optimizations involved",
            "There is no functional difference between them in modern Java",
            "Unchecked exceptions must always be caught in a try-catch block"
        ],
        "answerIndex": 0
    },
    "java-0299": {
        "options": [
            "A try block specifically designed for handling network timeout errors",
            "A try block that automatically retries the operation upon any failure",
            "A try block that auto-closes AutoCloseable resources when it exits",
            "A try block that sequentially attempts different algorithm strategies"
        ],
        "answerIndex": 2
    },
    "java-0297": {
        "options": [
            "Manual memory deallocation similar to malloc/free in C programs",
            "Automatic reclamation of memory from unreachable objects by the JVM",
            "Periodic cleanup of temporary files stored on the local disk",
            "Scheduled rotation and archival of application log file outputs"
        ],
        "answerIndex": 1
    },
    "java-0314": {
        "options": [
            "Making a variable constant and immutable after initialization",
            "Making a variable exist only during method scope execution",
            "Making a variable safely accessible from multiple concurrent threads",
            "Excluding a field from serialization via ObjectOutputStream"
        ],
        "answerIndex": 3
    },
    "java-0324": {
        "options": [
            "Classes are loaded in random order as the JVM finds them",
            "All referenced classes are loaded eagerly at JVM startup time",
            "ClassLoaders form a hierarchy, each delegating to its parent first",
            "Classes are loaded from disk only during the compilation phase"
        ],
        "answerIndex": 2
    },
    "java-0394": {
        "options": [
            "run() returns void with no checked exceptions; call() returns a value and can throw",
            "Callable cannot be submitted to any thread pool executor service",
            "Runnable is the newer of the two interfaces introduced in Java 8",
            "They are functionally identical interfaces with different package locations"
        ],
        "answerIndex": 0
    },

    # OS
    "os-0275": {
        "options": [
            "A CPU instruction for kernel-mode context switching operations",
            "A network node managing inter-process communication on the LAN",
            "A metadata structure storing permissions, size, and data block pointers",
            "A unique process identifier assigned by the operating system kernel"
        ],
        "answerIndex": 2
    },
    "os-0271": {
        "options": [
            "When critically low on memory, it selects and kills a process to free RAM",
            "It only logs warning messages about high memory usage to syslog",
            "It dynamically allocates additional swap space from available disk storage",
            "It terminates all running processes to prevent a total system crash"
        ],
        "answerIndex": 0
    },
    "os-0252": {
        "options": [
            "A slow program caused by inefficient algorithm implementation choices",
            "A special type of deadlock involving exactly two competing threads",
            "A gradual memory leak caused by unreleased heap allocations",
            "A bug where the outcome depends on unpredictable thread timing"
        ],
        "answerIndex": 3
    },
    "os-0276": {
        "options": [
            "All three I/O models wait identically for completion before returning",
            "Blocking I/O is always the preferred model for best performance",
            "Blocking waits; non-blocking returns immediately; async notifies via callback",
            "Asynchronous I/O is functionally the same as non-blocking I/O"
        ],
        "answerIndex": 2
    },
    "os-0267": {
        "options": [
            "A lock mechanism that prevents all context switches system-wide",
            "A lock used exclusively for managing distributed network resources",
            "A lock where the thread busy-waits in a loop checking lock availability",
            "A lock that creates and spins up new threads for parallel waiting"
        ],
        "answerIndex": 2
    },
    "os-0281": {
        "options": [
            "Signals and interrupts are identical mechanisms with different naming",
            "Interrupts are used only in user-space application programming contexts",
            "Signals are software notifications to processes; interrupts are hardware events",
            "Signals are always faster than interrupts due to kernel optimization"
        ],
        "answerIndex": 2
    },
    "os-0240": {
        "options": [
            "A web browser engine that renders HTML and CSS on the screen",
            "The core managing hardware resources, memory, processes, and syscalls",
            "A user-facing application for interacting with the file system",
            "A built-in text editor for editing system configuration file settings"
        ],
        "answerIndex": 1
    },
    "os-0391": {
        "options": [
            "A graphical desktop window in the display manager environment",
            "A command-line interface that interprets commands and talks to the kernel",
            "A type of volatile memory used for temporary data buffer storage",
            "The physical outer casing that protects internal computer hardware"
        ],
        "answerIndex": 1
    },
    "os-0242": {
        "options": [
            "A network timeout error caused by an expired TCP connection timer",
            "A fatal compiler error from invalid syntax in the source code",
            "An interrupt when a process accesses an unmapped virtual address",
            "A disk formatting error caused by corrupted filesystem metadata"
        ],
        "answerIndex": 2
    },
    "os-0237": {
        "options": [
            "Physical RAM installed directly on the motherboard of the machine",
            "Cloud-hosted storage accessible over the network via HTTP APIs",
            "A technique using disk to extend RAM, giving each process its own space",
            "CPU cache memory used for speeding up frequent data accesses"
        ],
        "answerIndex": 2
    },
    "os-0253": {
        "options": [
            "Fragmentation of disk blocks causing slower sequential read performance",
            "CPU overheating from sustained high-utilization compute workloads",
            "Spending most time swapping pages to disk instead of executing instructions",
            "Network congestion from excessive packet retransmissions on the link"
        ],
        "answerIndex": 2
    },
    "os-0283": {
        "options": [
            "A memory corruption bug caused by buffer overflow in kernel space",
            "Many threads woken simultaneously competing for one resource, wasting CPU",
            "A single runaway thread consuming all available CPU time on a core",
            "Too many threads creating a circular dependency causing total deadlock"
        ],
        "answerIndex": 1
    },
    "os-0265": {
        "options": [
            "Monolithic and microkernel architectures are functionally identical designs",
            "Microkernels are always faster due to reduced context switching overhead",
            "Monolithic: all services in kernel space; micro: only essentials in kernel",
            "Monolithic kernels cannot be compiled on modern 64-bit architectures"
        ],
        "answerIndex": 2
    },

    # System Design
    "systemdesign-0070": {
        "options": [
            "A distributed NoSQL database for storing API request metadata",
            "A physical network switch connecting backend server clusters together",
            "A frontend CSS framework for building responsive web user interfaces",
            "A single entry point that routes, authenticates, and rate-limits requests"
        ],
        "answerIndex": 3
    },
    "systemdesign-0082": {
        "options": [
            "A caching principle stating that cached data never becomes stale",
            "A load balancing strategy for distributing requests across web servers",
            "A tradeoff between consistency, atomicity, and overall system performance",
            "During a partition, you must choose between consistency and availability"
        ],
        "answerIndex": 3
    },
    "systemdesign-0110": {
        "options": [
            "SAGA is always faster than 2PC for all distributed transaction types",
            "2PC uses locking for strong consistency; SAGA uses compensating transactions",
            "They are the same protocol with different names across vendor implementations",
            "2PC operates without any coordinator node managing transaction participants"
        ],
        "answerIndex": 1
    },
    "systemdesign-0107": {
        "options": [
            "Through idempotent producers, transactional writes, and offset management",
            "By relying on TCP's built-in reliability and retransmission mechanisms",
            "By sending every message exactly three times to different broker partitions",
            "By storing all messages exclusively in RAM for immediate acknowledgment"
        ],
        "answerIndex": 0
    },
    "systemdesign-0092": {
        "options": [
            "Multiple hash functions on a bit array testing membership with no false negatives",
            "An in-place sorting algorithm optimized for partially ordered datasets",
            "A lossy compression algorithm designed for reducing image file sizes",
            "A machine learning model trained to filter incoming spam email messages"
        ],
        "answerIndex": 0
    },
    "systemdesign-0098": {
        "options": [
            "A gradual memory leak pattern caused by unclosed resource handles",
            "A request surge hitting the backend simultaneously when a cache expires",
            "A deadlock scenario in multithreaded systems with circular lock dependencies",
            "A type of distributed denial-of-service attack using amplification techniques"
        ],
        "answerIndex": 1
    },
    "systemdesign-0089": {
        "options": [
            "Optimistic checks at commit time; pessimistic locks the resource upfront",
            "Both approaches have identical behavior and interchangeable usage patterns",
            "Optimistic locking is always faster regardless of contention level involved",
            "Pessimistic locking uses no locking mechanism and relies on retries only"
        ],
        "answerIndex": 0
    },
    "systemdesign-0117": {
        "options": [
            "p99 measures the slowest 1% of requests, disproportionately affecting UX at scale",
            "Tail latency refers to the fastest response time observed in the system",
            "p99 latency is always exactly equal to the p50 median latency measurement",
            "Tail latency metrics only matter for offline batch processing job workloads"
        ],
        "answerIndex": 0
    },
    "systemdesign-0120": {
        "options": [
            "Adaptive capacity redistributes throughput from idle partitions to hot ones",
            "DynamoDB has no built-in mechanism for handling hot partition key problems",
            "It duplicates all data to every partition for uniform access distribution",
            "It rejects all write requests targeting partitions identified as hot"
        ],
        "answerIndex": 0
    },
    "systemdesign-0106": {
        "options": [
            "During a partition, writes can't propagate — reject writes (lose A) or serve stale (lose C)",
            "CAP is purely theoretical with no practical impact on real system design",
            "Network partitions are so rare in practice that they never actually happen",
            "Consistency and availability describe the same property using different terminology"
        ],
        "answerIndex": 0
    },
    "systemdesign-0101": {
        "options": [
            "Protocol Buffers over HTTP/2 provide lower latency and strong typing",
            "It only supports GET requests and cannot handle streaming workloads",
            "It is easier to debug interactively in the browser developer console",
            "It doesn't require any network connection to function between services"
        ],
        "answerIndex": 0
    },
    "systemdesign-0097": {
        "options": [
            "Single Leader Authority — one node coordinates all write operations exclusively",
            "Service Level Agreement — defines uptime guarantees the system must meet",
            "Server Logging Architecture — standardized framework for centralized log collection",
            "Structured Language API — a typed query interface for database interactions"
        ],
        "answerIndex": 1
    },
    "systemdesign-0065": {
        "options": [
            "The time delay between sending a request and receiving the response back",
            "The maximum amount of persistent data a single server can store on disk",
            "The encryption strength and key length of a secure TLS/SSL connection",
            "The total number of active servers deployed in a distributed cluster"
        ],
        "answerIndex": 0
    },
    "systemdesign-0076": {
        "options": [
            "A deprecated third-party library that needs version upgrade urgently",
            "A component whose failure brings down the entire system completely",
            "A slow API endpoint causing elevated latency in downstream requests",
            "A minor visual bug in the user interface affecting layout alignment"
        ],
        "answerIndex": 1
    },
    "systemdesign-0069": {
        "options": [
            "Deleting old records to free up database storage space periodically",
            "Copying data across multiple servers for redundancy and read scaling",
            "Encrypting data at rest using symmetric key encryption algorithms",
            "Normalizing tables to eliminate redundancy in relational schema design"
        ],
        "answerIndex": 1
    },
    "systemdesign-0068": {
        "options": [
            "A server that sits in front of backends and forwards client requests",
            "A database indexing strategy for optimizing complex join query performance",
            "A comparison-based sorting algorithm with O(n log n) average complexity",
            "A client-side JavaScript library for building single-page web applications"
        ],
        "answerIndex": 0
    },
    "systemdesign-0125": {
        "options": [
            "A distributed caching invalidation problem involving stale cache entries",
            "A shortest-path network routing algorithm used by interior gateway protocols",
            "A horizontal database sharding strategy based on consistent hash ranges",
            "Achieving consensus among nodes when some may be faulty or malicious"
        ],
        "answerIndex": 3
    },
    "systemdesign-0123": {
        "options": [
            "Reading data exclusively from a single designated partition replica node",
            "Always reading the most recently committed write from any available replica",
            "Ensuring query results are returned sorted in strict alphabetical ordering",
            "Ensuring reads respect causal ordering so effects follow their causes"
        ],
        "answerIndex": 3
    },

    # CN
    "cn-0138": {
        "options": [
            "A device that monitors and filters traffic based on security rules",
            "An asymmetric encryption protocol for securing data in transit",
            "A specialized router for inter-VLAN traffic forwarding and load balancing",
            "A distributed database system for storing network configuration data"
        ],
        "answerIndex": 0
    },
    "cn-0132": {
        "options": [
            "Forwarding packets between networks using routing table lookups and TTL",
            "Encrypting network traffic with TLS certificates between client and server",
            "Mapping an IP address to a MAC (hardware) address on a local network",
            "Mapping a domain name to an IP address through recursive DNS resolution"
        ],
        "answerIndex": 2
    },
    "cn-0133": {
        "options": [
            "IPv6 is noticeably slower than IPv4 due to larger header overhead",
            "IPv4 uses 32-bit addresses (~4B); IPv6 uses 128-bit (virtually unlimited)",
            "IPv6 only works over wireless Wi-Fi connections, not wired ethernet",
            "IPv4 supports built-in encryption but IPv6 removed that capability"
        ],
        "answerIndex": 1
    },
    "cn-0139": {
        "options": [
            "Internal Cache Memory Protocol — manages CPU cache line coherence",
            "Internet Control Message Protocol — error reporting and diagnostics like ping",
            "Integrated Circuit Monitoring Platform — tracks hardware component health",
            "Internet Connection Management Protocol — manages TCP connection lifecycle"
        ],
        "answerIndex": 1
    },
    "cn-0383": {
        "options": [
            "Hosting and serving static website content to end users via HTTP",
            "Receiving DNS queries and recursively resolving domain names to IPs",
            "Encrypting DNS traffic using DNS-over-HTTPS or DNS-over-TLS protocols",
            "Managing network switch port configurations and VLAN membership tables"
        ],
        "answerIndex": 1
    },
    "cn-0144": {
        "options": [
            "The fastest production server currently running on the local network",
            "The router IP a device uses to send traffic outside its local subnet",
            "The primary DNS server address used for domain name resolution queries",
            "The MAC hardware address of the network switch's management interface"
        ],
        "answerIndex": 1
    },
    "cn-0185": {
        "options": [
            "eBGP has faster convergence compared to iBGP in all deployment scenarios",
            "eBGP and iBGP operate on different TCP port numbers for their sessions",
            "iBGP uses UDP transport while eBGP uses reliable TCP transport exclusively",
            "eBGP runs between different ASes; iBGP runs within one AS, needing full mesh"
        ],
        "answerIndex": 3
    },
    "cn-0173": {
        "options": [
            "A DDoS mitigation technique using traffic scrubbing at network edges",
            "A method for splitting oversized TCP segments into smaller MTU chunks",
            "Source routing where the source encodes the path as ordered segment instructions",
            "A VPN tunneling protocol for establishing encrypted site-to-site connections"
        ],
        "answerIndex": 2
    },
    "cn-0164": {
        "options": [
            "Half-duplex and full-duplex are the same communication mode entirely",
            "Half-duplex is one direction at a time; full-duplex is simultaneous two-way",
            "Full-duplex uses exactly half the bandwidth of half-duplex communication",
            "Half-duplex is always faster due to reduced collision detection overhead"
        ],
        "answerIndex": 1
    },
    "cn-0154": {
        "options": [
            "A stateful packet inspection firewall for enterprise network perimeters",
            "A recursive DNS resolution algorithm for translating domain names",
            "A link-state IGP using Dijkstra's algorithm to compute shortest paths",
            "An application-layer protocol for reliable file transfer between hosts"
        ],
        "answerIndex": 2
    },
    "cn-0176": {
        "options": [
            "An algorithm that compresses HTTP headers to reduce request overhead",
            "Combines small TCP segments into larger ones; disable for latency-sensitive apps",
            "An encryption algorithm for securing small packets in transit on the wire",
            "A fragmentation algorithm that splits large packets for MTU compliance"
        ],
        "answerIndex": 1
    },
    "cn-0178": {
        "options": [
            "A volumetric DDoS attack technique that floods the target with traffic",
            "A method for encrypting network headers using symmetric key algorithms",
            "A checksum-based approach for detecting packet corruption during transit",
            "Packets enter a fixed bucket that leaks at a constant rate, smoothing bursts"
        ],
        "answerIndex": 3
    },
    "cn-0170": {
        "options": [
            "Routers exhaust their available memory by storing too many route entries",
            "Packet TTL values reach infinity causing infinite forwarding loop cycles",
            "Routers keep incrementing costs through each other, converging extremely slowly",
            "The routing table overflows its allocated memory space causing a crash"
        ],
        "answerIndex": 2
    },

    # Data Engineering
    "dataengineering-0348": {
        "options": [
            "Batch processes large volumes at scheduled intervals; stream processes continuously",
            "Stream processing cannot handle large data volumes due to memory constraints",
            "Batch processing is always faster regardless of the data volume being processed",
            "They are identical approaches using different terminology across vendor platforms"
        ],
        "answerIndex": 0
    },
    "dataengineering-0343": {
        "options": [
            "Removing exact duplicate records from the dataset before join processing",
            "Adding a random suffix to the skewed key, distributing it across partitions",
            "Adding cryptographic salt to encrypt and protect sensitive join key data",
            "Compressing join keys using variable-length encoding to reduce shuffle size"
        ],
        "answerIndex": 1
    },
    "dataengineering-0342": {
        "options": [
            "When data is encrypted using different keys across separate partitions",
            "When data contains spelling errors causing incorrect aggregation results",
            "When data is sorted in the wrong order across distributed partition files",
            "When data is unevenly distributed across partitions, creating straggler tasks"
        ],
        "answerIndex": 3
    },
    "dataengineering-0353": {
        "options": [
            "An encryption timestamp attached to each event record for audit trails",
            "A timestamp marking the boundary below which all events have arrived",
            "A visible annotation rendered on real-time dashboard chart visualizations",
            "A digital signature authenticating the origin and integrity of event data"
        ],
        "answerIndex": 1
    },
    "dataengineering-0355": {
        "options": [
            "A multi-dimensional clustering that co-locates related data enabling skipping",
            "A file compression technique using zlib for reducing parquet file sizes",
            "An alphabetical sorting strategy applied to string columns in the dataset",
            "A B-tree based database index structure for accelerating point lookups"
        ],
        "answerIndex": 0
    },
    "dataengineering-0397": {
        "options": [
            "A compressed table format that reduces storage for cold analytical data",
            "A specialized index type for accelerating full-text search query operations",
            "A precomputed query result stored as a table, refreshed periodically on demand",
            "A regular view that re-executes its underlying query on every access attempt"
        ],
        "answerIndex": 2
    },

    # DSA
    "dsa-0058": {
        "options": [
            "Compress data using entropy-based encoding for efficient storage utilization",
            "Sort data faster using cache-oblivious algorithms that minimize page faults",
            "Access any previous version of the structure after modifications are made",
            "Store all data structures to persistent disk for crash recovery purposes"
        ],
        "answerIndex": 2
    },
    "dsa-0060": {
        "options": [
            "Floyd's cycle detection (tortoise and hare) on the index-value mapping",
            "XOR all elements together and extract the duplicate from the result",
            "Binary search on the value range and count elements in each half",
            "Sort the array in-place first then scan for adjacent duplicates found"
        ],
        "answerIndex": 0
    },
}

# Apply rewrites
rewritten = 0
for q in questions:
    qid = q["id"]
    if qid in REWRITES:
        q["options"] = REWRITES[qid]["options"]
        q["answerIndex"] = REWRITES[qid]["answerIndex"]
        rewritten += 1

# Write back
with open(OUTPUT, "w") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

# Stats after
with open(OUTPUT) as f:
    questions = json.load(f)

total = 0
correct_longer = 0
for q in questions:
    opts = q["options"]
    ci = q["answerIndex"]
    correct_len = len(opts[ci])
    wrong_lens = [len(opts[i]) for i in range(len(opts)) if i != ci]
    total += 1
    if correct_len > max(wrong_lens):
        correct_longer += 1

print(f"Rewrote: {rewritten} questions")
print(f"Correct answer still longest: {correct_longer}/{total} ({correct_longer*100//total}%)")
avg_correct = sum(len(q["options"][q["answerIndex"]]) for q in questions) / total
avg_wrong = sum(
    sum(len(q["options"][i]) for i in range(len(q["options"])) if i != q["answerIndex"])
    for q in questions
) / (total * 3)
print(f"Avg correct len: {avg_correct:.1f}")
print(f"Avg wrong len: {avg_wrong:.1f}")
