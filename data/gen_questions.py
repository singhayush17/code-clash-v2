#!/usr/bin/env python3
"""Generate a high-quality question bank of 400+ real interview-style MCQs."""

import json
import random

random.seed(42)

questions = []

# Helper: shuffles options and returns (shuffled_options, correct_index)
def add(cat, diff, prompt, correct, wrongs, explanation, tags=None):
    opts = wrongs + [correct]
    random.shuffle(opts)
    q = {
        "id": f"{cat.lower().replace(' ','').replace('/','')}-{len(questions)+1:04d}",
        "category": cat,
        "difficulty": diff,
        "prompt": prompt,
        "options": opts,
        "answerIndex": opts.index(correct),
        "explanation": explanation,
    }
    if tags:
        q["tags"] = tags
    questions.append(q)


# =============================================================================
#  DSA — 60 questions
# =============================================================================

# Easy (20)
add("DSA", "easy", "What is the time complexity of accessing an element by index in an array?",
    "O(1)", ["O(n)", "O(log n)", "O(n log n)"],
    "Arrays use contiguous memory, so index lookup is a single address calculation.", ["Google", "Amazon"])

add("DSA", "easy", "Which data structure uses FIFO (First In, First Out) ordering?",
    "Queue", ["Stack", "Binary Tree", "Hash Map"],
    "A queue processes elements in the order they were added.", ["TCS", "Infosys"])

add("DSA", "easy", "What data structure would you use to check if parentheses are balanced?",
    "Stack", ["Queue", "Linked List", "Heap"],
    "A stack naturally matches opening and closing brackets using push/pop.", ["Amazon", "Microsoft"])

add("DSA", "easy", "In a singly linked list, what is the time to insert at the head?",
    "O(1)", ["O(n)", "O(log n)", "O(n²)"],
    "You simply update the head pointer to the new node.", ["Wipro", "Cognizant"])

add("DSA", "easy", "Which sorting algorithm has best-case O(n) when the array is nearly sorted?",
    "Insertion Sort", ["Merge Sort", "Quick Sort", "Heap Sort"],
    "Insertion sort only shifts a few elements when data is almost sorted.", ["Flipkart", "Paytm"])

add("DSA", "easy", "What is the space complexity of a recursive Fibonacci implementation without memoization?",
    "O(n)", ["O(1)", "O(n²)", "O(2^n)"],
    "The call stack depth is at most n. The time complexity is O(2^n), but space is O(n).", ["Goldman Sachs"])

add("DSA", "easy", "A hash table with no collisions provides what average lookup time?",
    "O(1)", ["O(n)", "O(log n)", "O(n log n)"],
    "Hashing directly maps a key to a bucket in constant time.", ["Amazon", "Google"])

add("DSA", "easy", "What is the maximum number of nodes at level k in a binary tree?",
    "2^k", ["k", "2k", "k²"],
    "Each level doubles the number of nodes: level 0 has 1, level 1 has 2, etc.", ["Microsoft"])

add("DSA", "easy", "Which traversal visits the root node first, then left subtree, then right?",
    "Pre-order", ["In-order", "Post-order", "Level-order"],
    "Pre-order is Root → Left → Right.", ["Accenture", "TCS"])

add("DSA", "easy", "What does BFS use internally to track which nodes to visit next?",
    "Queue", ["Stack", "Priority Queue", "Deque"],
    "BFS explores level by level using a FIFO queue.", ["Meta", "Google"])

add("DSA", "easy", "In a max-heap, where is the largest element always located?",
    "At the root", ["At a leaf", "At the last index", "At the middle"],
    "The heap property ensures the root is always the maximum.", ["Oracle", "SAP"])

add("DSA", "easy", "What is the worst-case time complexity of linear search?",
    "O(n)", ["O(1)", "O(log n)", "O(n log n)"],
    "In the worst case, you must check every element.", ["Infosys", "Wipro"])

add("DSA", "easy", "Which of these is NOT a stable sorting algorithm?",
    "Heap Sort", ["Merge Sort", "Bubble Sort", "Insertion Sort"],
    "Heap Sort can rearrange equal elements due to its swap-based extraction.", ["Amazon"])

add("DSA", "easy", "What is the time complexity of removing an element from the front of an ArrayList (Java)?",
    "O(n)", ["O(1)", "O(log n)", "O(n log n)"],
    "All elements after the removed one must be shifted left.", ["JP Morgan", "Barclays"])

add("DSA", "easy", "A binary search requires the input to be:",
    "Sorted", ["Unique", "Positive", "Of equal length"],
    "Binary search divides the search space assuming sorted order.")

add("DSA", "easy", "What is the minimum number of edges in a connected graph with n nodes?",
    "n - 1", ["n", "n/2", "n²"],
    "A tree (minimally connected graph) uses exactly n−1 edges.", ["Google"])

add("DSA", "easy", "Which data structure is best for implementing an undo feature?",
    "Stack", ["Queue", "Array", "Linked List"],
    "Undo naturally follows LIFO: the last action is undone first.", ["Adobe", "Atlassian"])

add("DSA", "easy", "What is 5! (5 factorial)?",
    "120", ["60", "24", "720"],
    "5! = 5 × 4 × 3 × 2 × 1 = 120.")

add("DSA", "easy", "A doubly linked list differs from a singly linked list by having:",
    "Pointers to both the next and previous nodes", ["Two data fields per node", "A circular structure", "Indexed access"],
    "Each node holds references in both directions.")

add("DSA", "easy", "In Big-O notation, what does O(1) mean?",
    "Constant time regardless of input size", ["Linear time", "Logarithmic time", "Time proportional to input squared"],
    "O(1) operations don't depend on n.")

# Medium (20)
add("DSA", "medium", "What is the worst-case time complexity of QuickSort?",
    "O(n²)", ["O(n log n)", "O(n)", "O(log n)"],
    "When the pivot is always the smallest or largest element, partitions are maximally unbalanced.", ["Google", "Amazon", "Meta"])

add("DSA", "medium", "To find the kth largest element in an unsorted array efficiently, which approach is optimal?",
    "Min-heap of size k", ["Sort the entire array", "Binary search", "Linear scan k times"],
    "Maintain a min-heap of k elements. If new element > heap root, replace and heapify. O(n log k).", ["Amazon", "Facebook", "Apple"])

add("DSA", "medium", "What is the time complexity of Dijkstra's algorithm with a min-heap?",
    "O((V + E) log V)", ["O(V²)", "O(V × E)", "O(E log E)"],
    "Each vertex is extracted once from the heap (log V), and each edge relaxes once.", ["Google", "Uber"])

add("DSA", "medium", "Which algorithm finds the shortest path in graphs with negative edge weights (no negative cycles)?",
    "Bellman-Ford", ["Dijkstra's", "Prim's", "Kruskal's"],
    "Bellman-Ford relaxes all edges V−1 times and can handle negative weights.", ["Amazon", "Bloomberg"])

add("DSA", "medium", "What is the amortized time complexity of appending to a dynamic array (like Python list)?",
    "O(1)", ["O(n)", "O(log n)", "O(n²)"],
    "Most appends are O(1). Occasional resizing is O(n), but amortized across all appends it averages to O(1).", ["Google", "Meta"])

add("DSA", "medium", "In a BST, what is the time complexity of searching in the average case?",
    "O(log n)", ["O(1)", "O(n)", "O(n log n)"],
    "A balanced BST halves the search space at each comparison.", ["Microsoft", "Amazon"])

add("DSA", "medium", "What data structure would you use to efficiently find the median of a stream of numbers?",
    "Two heaps (max-heap + min-heap)", ["Sorted array", "Single priority queue", "Hash map"],
    "A max-heap for the lower half and min-heap for the upper half gives O(1) median access.", ["Apple", "Facebook", "Google"])

add("DSA", "medium", "Topological sort is applicable to which type of graph?",
    "Directed Acyclic Graph (DAG)", ["Undirected graph", "Cyclic directed graph", "Weighted undirected graph"],
    "Topological ordering requires no cycles and directed edges.", ["Amazon", "Microsoft", "Atlassian"])

add("DSA", "medium", "In the two-pointer technique on a sorted array (finding pairs that sum to X), what is the time complexity?",
    "O(n)", ["O(n²)", "O(n log n)", "O(log n)"],
    "One pointer starts at each end and they move inward, scanning the array once.", ["Google", "Facebook"])

add("DSA", "medium", "What is the worst-case time complexity of searching in a hash table with chaining?",
    "O(n)", ["O(1)", "O(log n)", "O(n log n)"],
    "If all keys hash to the same bucket, you must traverse a linked list of n elements.", ["Goldman Sachs", "Morgan Stanley"])

add("DSA", "medium", "Which traversal of a BST gives elements in sorted order?",
    "In-order", ["Pre-order", "Post-order", "Level-order"],
    "In-order traversal visits Left → Root → Right, which is ascending for BSTs.", ["Amazon", "Microsoft"])

add("DSA", "medium", "What is the time complexity of building a heap from an unsorted array?",
    "O(n)", ["O(n log n)", "O(n²)", "O(log n)"],
    "Bottom-up heap construction (Floyd's algorithm) runs in linear time.", ["Google", "Uber"])

add("DSA", "medium", "What problem does Kadane's algorithm solve?",
    "Maximum subarray sum", ["Longest common subsequence", "Shortest path", "Minimum spanning tree"],
    "Kadane's algorithm finds the contiguous subarray with the largest sum in O(n).", ["Amazon", "Microsoft", "Goldman Sachs"])

add("DSA", "medium", "Merge Sort has which space complexity?",
    "O(n)", ["O(1)", "O(log n)", "O(n²)"],
    "Merge sort requires additional arrays for merging, proportional to input size.", ["Apple", "Google"])

add("DSA", "medium", "Which data structure supports O(log n) insert, delete, and search with sorted order?",
    "Balanced BST (AVL / Red-Black Tree)", ["Hash table", "Array", "Linked list"],
    "Self-balancing BSTs maintain height O(log n) guaranteeing efficient operations.", ["Amazon", "Bloomberg"])

add("DSA", "medium", "What is the time complexity of counting sort?",
    "O(n + k) where k is the range of input values", ["O(n log n)", "O(n²)", "O(n)"],
    "Counting sort counts occurrences and reconstructs the output in linear passes.", ["Google"])

add("DSA", "medium", "In a graph, what does a 'back edge' during DFS indicate?",
    "The presence of a cycle", ["A disconnected component", "A bipartite graph", "A shortest path"],
    "A back edge connects a node to one of its ancestors, creating a cycle.", ["Meta", "Amazon"])

add("DSA", "medium", "What is the purpose of a Trie data structure?",
    "Efficient prefix-based string searching", ["Sorting integers", "Balancing binary trees", "Hashing strings"],
    "Tries store strings character by character, enabling O(L) prefix lookups where L is word length.", ["Google", "Amazon", "Microsoft"])

add("DSA", "medium", "The 'sliding window' technique is most useful for:",
    "Finding optimal subarrays/substrings of a given constraint", ["Sorting data", "Graph traversal", "Tree balancing"],
    "Sliding window maintains a window that grows/shrinks to meet constraints, avoiding recomputation.", ["Amazon", "Facebook", "Uber"])

add("DSA", "medium", "What is the key difference between BFS and DFS?",
    "BFS uses a queue and explores level-by-level; DFS uses a stack and goes deep first", ["BFS is faster than DFS", "DFS always finds the shortest path", "BFS cannot detect cycles"],
    "BFS guarantees shortest path in unweighted graphs; DFS is useful for backtracking problems.", ["Microsoft", "Google"])

# Hard (20)
add("DSA", "hard", "What is the time complexity of the optimal algorithm for finding the Longest Common Subsequence (LCS) of two strings of length m and n?",
    "O(m × n)", ["O(m + n)", "O(m × n²)", "O(2^(m+n))"],
    "The DP table has m×n cells, each computed in O(1).", ["Google", "Amazon", "Microsoft"])

add("DSA", "hard", "In Union-Find with path compression and union by rank, what is the amortized time per operation?",
    "O(α(n)) — nearly constant (inverse Ackermann)", ["O(log n)", "O(1) strict", "O(n)"],
    "α(n) is the inverse Ackermann function, which grows incredibly slowly — effectively constant.", ["Google", "Facebook"])

add("DSA", "hard", "Dijkstra's algorithm fails when the graph has:",
    "Negative edge weights", ["Self-loops", "Directed edges", "More than 1000 nodes"],
    "Negative edges can make an already-finalized node's distance incorrect.", ["Uber", "Google"])

add("DSA", "hard", "What is the time complexity of finding articulation points (cut vertices) in a graph?",
    "O(V + E)", ["O(V²)", "O(V × E)", "O(V log V)"],
    "Tarjan's algorithm uses a single DFS pass to find all articulation points.", ["Amazon", "Google"])

add("DSA", "hard", "Which dynamic programming optimization reduces 2D DP space to O(n)?",
    "Space optimization using two rows (rolling array)", ["Memoization", "Divide and conquer", "Branch and bound"],
    "If each row depends only on the previous row, you only need to store two rows at a time.", ["Google", "Meta"])

add("DSA", "hard", "What is the time complexity of the Floyd-Warshall all-pairs shortest path algorithm?",
    "O(V³)", ["O(V²)", "O(V² log V)", "O(V × E)"],
    "Three nested loops over V vertices each give O(V³).", ["Amazon", "Bloomberg"])

add("DSA", "hard", "A Segment Tree supports range queries and point updates in:",
    "O(log n) per operation", ["O(1) per operation", "O(n) per operation", "O(√n) per operation"],
    "The tree has height O(log n), and queries/updates traverse one root-to-leaf path.", ["Google", "Codeforces"])

add("DSA", "hard", "What is the computational class of the Travelling Salesman Problem (finding optimal tour)?",
    "NP-hard", ["O(n log n)", "O(n²)", "P (polynomial)"],
    "No known polynomial algorithm exists. The brute-force approach is O(n!), DP gives O(n² × 2^n).", ["Google", "Microsoft"])

add("DSA", "hard", "What does Manacher's algorithm solve?",
    "Finding the longest palindromic substring in O(n)", ["Sorting strings alphabetically", "Finding shortest path", "Computing LCS"],
    "Manacher's algorithm exploits palindrome symmetry properties to achieve linear time.", ["Amazon", "Google"])

add("DSA", "hard", "In a Suffix Array, what is the time to search for a pattern of length m in a text of length n?",
    "O(m log n)", ["O(n × m)", "O(m + n)", "O(n²)"],
    "Binary search on the suffix array takes O(log n) comparisons, each O(m).", ["Google"])

add("DSA", "hard", "What is the maximum flow algorithm that runs in O(V × E²)?",
    "Edmonds-Karp (BFS-based Ford-Fulkerson)", ["Dijkstra's", "Bellman-Ford", "Prim's"],
    "Edmonds-Karp uses BFS to find augmenting paths, guaranteeing O(VE²) time.", ["Google", "Amazon"])

add("DSA", "hard", "A Fenwick Tree (Binary Indexed Tree) supports prefix sum queries in:",
    "O(log n)", ["O(1)", "O(n)", "O(√n)"],
    "BIT traverses at most O(log n) indices using bit manipulation.", ["Google", "Meta"])

add("DSA", "hard", "What problem does KMP (Knuth-Morris-Pratt) algorithm solve efficiently?",
    "Pattern matching in strings in O(n + m) time", ["Graph shortest path", "Sorting", "Matrix multiplication"],
    "KMP preprocesses the pattern to avoid redundant comparisons, achieving linear time.", ["Amazon", "Microsoft"])

add("DSA", "hard", "What is the tight bound for comparison-based sorting?",
    "Ω(n log n)", ["Ω(n)", "Ω(n²)", "Ω(log n)"],
    "Any comparison sort must make at least n log n comparisons in the worst case (decision tree argument).", ["Google", "Jane Street"])

add("DSA", "hard", "In graph theory, Kosaraju's algorithm finds:",
    "All Strongly Connected Components (SCCs)", ["Minimum spanning tree", "Shortest path", "Bipartite matching"],
    "It uses two DFS passes — one on the original graph and one on the transposed graph.", ["Amazon", "Google"])

add("DSA", "hard", "What data structure answers 'what is the minimum in range [l, r]?' in O(1) after O(n log n) preprocessing?",
    "Sparse Table", ["Segment Tree", "Fenwick Tree", "Hash Map"],
    "Sparse Table precomputes answers for all power-of-2 ranges, enabling O(1) overlap-friendly queries.", ["Google", "Codeforces"])

add("DSA", "hard", "What is the time complexity of multiplying two n×n matrices using Strassen's algorithm?",
    "O(n^2.807)", ["O(n³)", "O(n²)", "O(n² log n)"],
    "Strassen reduces 8 recursive multiplications to 7, giving the exponent log₂(7) ≈ 2.807.", ["Google", "Microsoft"])

add("DSA", "hard", "A persistent data structure allows you to:",
    "Access any previous version of the structure after modifications", ["Store data to disk", "Compress data", "Sort data faster"],
    "Persistent structures preserve all previous versions, often using path copying.", ["Jane Street", "Google"])

add("DSA", "hard", "What is the time complexity of the A* search algorithm in the worst case?",
    "O(b^d) where b is branching factor and d is depth", ["O(V + E)", "O(V log V)", "O(n²)"],
    "A* has exponential worst case, but a good heuristic makes it much faster in practice.", ["Google", "Uber"])

add("DSA", "hard", "What trick lets you find the duplicate in an array of n+1 integers in range [1, n] using O(1) space?",
    "Floyd's cycle detection (tortoise and hare) on the index-value mapping", ["XOR all elements", "Sort and scan", "Binary search on value"],
    "Treat array values as 'next pointers'. The duplicate creates a cycle, detectable in O(n) time.", ["Amazon", "Google", "Microsoft"])


# =============================================================================
#  System Design — 65 questions
# =============================================================================

# Easy (20)
add("System Design", "easy", "What is the primary purpose of a load balancer?",
    "Distributing incoming traffic across multiple servers", ["Encrypting database connections", "Compiling source code", "Managing DNS records"],
    "Load balancers prevent any single server from becoming a bottleneck.", ["Amazon", "Google"])

add("System Design", "easy", "What is horizontal scaling?",
    "Adding more machines to handle increased load", ["Adding more RAM to a single machine", "Optimizing database queries", "Reducing code complexity"],
    "Horizontal scaling (scale-out) adds nodes; vertical scaling (scale-up) upgrades a single machine.")

add("System Design", "easy", "What does a CDN (Content Delivery Network) do?",
    "Caches and serves static content from servers geographically closer to users", ["Runs machine learning models", "Manages database migrations", "Compiles JavaScript"],
    "CDNs reduce latency by serving content from edge locations.", ["Cloudflare", "Akamai"])

add("System Design", "easy", "What is the difference between SQL and NoSQL databases?",
    "SQL enforces structured schemas with ACID; NoSQL offers flexible schemas optimized for scale", ["SQL is faster than NoSQL always", "NoSQL cannot store data permanently", "SQL only works on Linux"],
    "SQL suits relational data; NoSQL suits high-scale, variable-structure data.")

add("System Design", "easy", "What does 'latency' mean in system design?",
    "The time delay between a request being sent and the response being received", ["The maximum data a server can store", "The number of servers in a cluster", "The encryption strength of a connection"],
    "Lower latency means faster responses for users.")

add("System Design", "easy", "What is a message queue used for?",
    "Asynchronously decoupling producers and consumers of data", ["Sorting database records", "Serving static HTML files", "Validating user passwords"],
    "Message queues (like RabbitMQ, SQS) buffer tasks so services can process at their own pace.", ["Amazon", "Uber"])

add("System Design", "easy", "What does 'throughput' measure?",
    "The number of requests or operations a system can handle per unit of time", ["The physical size of a server", "The color depth of an image", "The amount of RAM used"],
    "High throughput = the system can process many requests concurrently.")

add("System Design", "easy", "What is a reverse proxy?",
    "A server that sits in front of backend servers and forwards client requests to them", ["A client-side JavaScript library", "A database indexing strategy", "A sorting algorithm"],
    "Nginx and HAProxy are popular reverse proxies.", ["Cloudflare", "Netflix"])

add("System Design", "easy", "What is database replication?",
    "Copying data across multiple database servers for redundancy and read performance", ["Deleting old records", "Encrypting data at rest", "Normalizing tables"],
    "Replication improves availability — if one node fails, others serve requests.", ["Amazon", "Google"])

add("System Design", "easy", "What is an API gateway?",
    "A single entry point that routes, authenticates, and rate-limits requests to backend microservices", ["A physical network switch", "A type of database", "A CSS framework"],
    "API gateways centralize cross-cutting concerns like auth, logging, and throttling.", ["Amazon", "Netflix"])

add("System Design", "easy", "What does REST stand for?",
    "REpresentational State Transfer", ["Remote Execution of Server Tasks", "Real-time Event Streaming Technology", "Redundant Error-Safe Transport"],
    "REST is an architectural style using HTTP verbs (GET, POST, PUT, DELETE) on resources.")

add("System Design", "easy", "What is vertical scaling?",
    "Adding more CPU, RAM, or storage to an existing server", ["Adding more servers to a cluster", "Splitting a database into shards", "Deploying across multiple regions"],
    "Vertical scaling is simpler but has physical hardware limits.")

add("System Design", "easy", "What is a health check in the context of load balancing?",
    "A periodic ping to verify backend servers are alive and responsive", ["A security audit of the codebase", "A memory leak detection tool", "A database backup process"],
    "Unhealthy servers are removed from the pool until they recover.")

add("System Design", "easy", "What is the purpose of caching?",
    "Storing frequently accessed data in fast storage to reduce repeated expensive computations or lookups", ["Permanently archiving old data", "Encrypting user passwords", "Compressing images"],
    "Caches (Redis, Memcached) dramatically reduce database load and response times.", ["Amazon", "Netflix"])

add("System Design", "easy", "What is a webhook?",
    "An HTTP callback that notifies your server when an event occurs in another service", ["A type of SQL JOIN", "A CSS animation", "A cloud storage bucket"],
    "Webhooks enable event-driven architectures without polling.", ["Stripe", "GitHub"])

add("System Design", "easy", "What is the 'single point of failure' (SPOF) problem?",
    "A component whose failure brings down the entire system", ["A minor bug in the UI", "A slow API endpoint", "A deprecated library"],
    "Redundancy and failover mechanisms eliminate SPOFs.")

add("System Design", "easy", "What is the purpose of an index in a database?",
    "Speed up read queries by creating a data structure (e.g., B-Tree) for faster lookups", ["Encrypt data at rest", "Compress table rows", "Replicate data across regions"],
    "Indexes trade extra write overhead and storage for much faster reads.", ["Amazon", "Google"])

add("System Design", "easy", "What is a microservice?",
    "A small, independently deployable service that handles a specific business capability", ["A front-end framework", "A type of database query", "A single monolithic application"],
    "Microservices enable teams to develop, deploy, and scale services independently.", ["Netflix", "Uber"])

add("System Design", "easy", "What is rate limiting?",
    "Restricting the number of requests a client can make in a given time window", ["Increasing server CPU speed", "Reducing image file sizes", "Compiling code faster"],
    "Rate limiting protects servers from abuse and ensures fair usage.", ["Stripe", "Cloudflare"])

add("System Design", "easy", "What is eventual consistency?",
    "A model where replicas may temporarily have different data but will converge over time", ["Immediate consistency at all times", "Data is never stored persistently", "Queries always return errors first"],
    "Many NoSQL systems use eventual consistency for better availability and partition tolerance.", ["Amazon"])

# Medium (25)
add("System Design", "medium", "In Apache Kafka, what happens if there are more consumers in a group than partitions?",
    "The excess consumers sit idle (each partition is consumed by at most one consumer per group)", ["Messages are duplicated to all consumers", "Kafka auto-creates new partitions", "An error is thrown and consumers crash"],
    "Partitions are the unit of parallelism. Extra consumers serve as standby replicas.", ["LinkedIn", "Uber", "Confluent"])

add("System Design", "medium", "What is the CAP theorem?",
    "In a distributed system experiencing a network partition, you must choose between Consistency and Availability", ["Caching Always Performs — caches never go stale", "Consistency, Atomicity, and Performance tradeoff", "A load balancing strategy for web servers"],
    "CAP states that C, A, and P cannot all be guaranteed simultaneously during a partition.", ["Amazon", "Google"])

add("System Design", "medium", "What is consistent hashing and why is it useful?",
    "A hashing scheme where adding/removing nodes only redistributes ~1/N of the keys", ["A hash function that never has collisions", "A way to sort data alphabetically", "An encryption algorithm"],
    "Regular hashing remaps almost all keys on resize. Consistent hashing minimizes disruption.", ["Discord", "Netflix", "Amazon"])

add("System Design", "medium", "What is database sharding?",
    "Horizontally partitioning data across multiple database instances based on a shard key", ["Vertically splitting tables into separate columns", "Backing up data", "Indexing all columns"],
    "Sharding distributes write load but makes cross-shard queries complex.", ["Facebook", "Airbnb", "Pinterest"])

add("System Design", "medium", "What is the difference between a token bucket and a leaky bucket rate limiter?",
    "Token bucket allows controlled bursts; leaky bucket enforces a strict constant output rate", ["They are identical", "Token bucket is for databases; leaky bucket is for networks", "Leaky bucket allows bursts; token bucket does not"],
    "Token bucket accumulates tokens over time, allowing temporary burst capacity.", ["Stripe", "Cloudflare"])

add("System Design", "medium", "What is an idempotent API operation?",
    "An operation that produces the same result regardless of how many times it is called", ["An operation that is always fast", "An operation that requires no authentication", "An operation that only works on GET requests"],
    "PUT and DELETE are typically idempotent. Idempotency makes retries safe after timeouts.", ["Stripe", "Amazon"])

add("System Design", "medium", "In Redis, why is the KEYS command dangerous in production?",
    "It blocks Redis's single-threaded event loop, scanning all keys and making the server unresponsive", ["It permanently deletes all keys", "It uses excessive network bandwidth", "It corrupts the AOF log"],
    "Use SCAN instead for incremental, non-blocking iteration.", ["Twitter", "Stripe", "Microsoft"])

add("System Design", "medium", "What is a write-ahead log (WAL)?",
    "A log where changes are recorded before being applied to the database, ensuring crash recovery", ["A cache invalidation strategy", "A load balancing technique", "A message queue protocol"],
    "WAL guarantees durability — after a crash, the log can replay uncommitted changes.", ["PostgreSQL", "Google", "Amazon"])

add("System Design", "medium", "What is the difference between optimistic and pessimistic locking?",
    "Optimistic assumes no conflict and checks at commit; pessimistic locks the resource upfront", ["Optimistic is always faster", "Pessimistic uses no locking at all", "They have the same behavior"],
    "Optimistic locking uses version numbers; pessimistic uses explicit locks.", ["Google", "Goldman Sachs"])

add("System Design", "medium", "What is a circuit breaker pattern in microservices?",
    "Automatically stopping requests to a failing downstream service to prevent cascading failures", ["A way to split databases into shards", "A caching strategy", "A load balancing algorithm"],
    "After too many failures, the circuit 'opens' and returns errors immediately without calling the service.", ["Netflix", "Amazon"])

add("System Design", "medium", "What is backpressure?",
    "A mechanism to slow down a fast producer when consumers cannot keep up", ["A type of data compression", "A DNS resolution strategy", "A database normalization form"],
    "Without backpressure, queues grow unboundedly, leading to OOM crashes.", ["Uber", "Netflix"])

add("System Design", "medium", "How does a Bloom filter work?",
    "It uses multiple hash functions on a bit array to test set membership with possible false positives but no false negatives", ["It filters spam emails", "It compresses images", "It sorts data in-place"],
    "Bloom filters are space-efficient for large datasets where occasional false positives are acceptable.", ["Google", "Facebook", "Akamai"])

add("System Design", "medium", "What is the difference between a leader-follower and a leaderless replication model?",
    "Leader-follower routes writes to one node; leaderless allows writes to any node using quorum reads/writes", ["They are synonymous", "Leaderless always has lower latency", "Leader-follower cannot handle reads"],
    "DynamoDB uses leaderless (quorum); PostgreSQL uses leader-follower.", ["Amazon", "Google"])

add("System Design", "medium", "What is a dead-letter queue?",
    "A queue where messages that cannot be processed after multiple retries are sent for inspection", ["A queue that automatically deletes old messages", "A queue for high-priority messages", "A debugging tool for DNS"],
    "Dead-letter queues prevent poison messages from blocking normal queue processing.", ["Amazon", "Uber"])

add("System Design", "medium", "What is the fan-out problem in social media system design?",
    "When a popular user posts, push notifications must be delivered to millions of followers simultaneously", ["When a database has too many indexes", "When a server runs out of disk space", "When a CDN cache expires"],
    "Fan-out on write precomputes timelines; fan-out on read fetches at query time.", ["Twitter", "Facebook", "Instagram"])

add("System Design", "medium", "What is connection pooling?",
    "Reusing a set of pre-established database connections instead of creating new ones per request", ["Encrypting network connections", "Splitting traffic across data centers", "Compressing HTTP responses"],
    "Connection pooling reduces the overhead of TCP handshakes and authentication per query.", ["Amazon", "Google"])

add("System Design", "medium", "In system design, what does 'SLA' stand for and why does it matter?",
    "Service Level Agreement — defines uptime guarantees (e.g., 99.99%) the system must meet", ["Structured Language API", "Server Logging Architecture", "Single Leader Authority"],
    "Violating SLAs can result in financial penalties and customer churn.", ["Amazon", "Google", "Microsoft"])

add("System Design", "medium", "What is the 'thundering herd' problem?",
    "A surge of requests hitting a backend simultaneously when a cache expires, overloading the system", ["A type of distributed denial-of-service attack", "A memory leak pattern", "A deadlock in multithreaded systems"],
    "Solutions include cache stampede locks, staggered TTLs, and background refresh.", ["Facebook", "Netflix"])

add("System Design", "medium", "What is data partitioning by range vs. by hash?",
    "Range partitioning keeps ordered data together; hash partitioning distributes data uniformly but loses ordering", ["They are identical methods", "Hash is always better", "Range partitioning doesn't work with SQL"],
    "Range is good for range queries; hash avoids hotspots.", ["Amazon", "Google"])

add("System Design", "medium", "What is event sourcing?",
    "Storing every state change as an immutable event instead of only storing the current state", ["A way to remove old events from logs", "A type of load balancing", "An encryption method"],
    "Event sourcing enables time-travel debugging and rebuilding state by replaying events.", ["Goldman Sachs", "Uber"])

add("System Design", "medium", "Why is gRPC preferred over REST for internal microservice communication?",
    "It uses Protocol Buffers (binary serialization) over HTTP/2, providing lower latency and strong typing", ["It is easier to debug in the browser", "It supports only GET requests", "It doesn't require a network connection"],
    "gRPC also supports bidirectional streaming natively.", ["Google", "Square", "Lyft"])

add("System Design", "medium", "What is a read replica?",
    "A copy of the primary database that serves read queries to offload the primary", ["A backup taken nightly", "A replica that only stores metadata", "A copy that handles all writes"],
    "Read replicas improve read throughput but have replication lag.", ["Amazon", "Google"])

add("System Design", "medium", "What is the primary tradeoff of using a cache?",
    "Data staleness — cached data may become outdated if the source changes", ["Slower read times", "Higher disk usage", "Increased network bandwidth"],
    "Cache invalidation ('the two hardest things in CS') must be handled carefully.", ["Facebook", "Netflix"])

add("System Design", "medium", "What is server-sent events (SSE) vs WebSocket?",
    "SSE is unidirectional (server-to-client) over HTTP; WebSocket is bidirectional over a persistent TCP connection", ["They are identical protocols", "SSE is faster than WebSocket always", "WebSocket only works on mobile"],
    "SSE is simpler for notifications/feeds; WebSocket is needed for real-time bidirectional communication (chat, games).")

add("System Design", "medium", "What problem does a distributed lock (e.g., Redlock) solve?",
    "Ensuring mutual exclusion across multiple services or instances in a distributed system", ["Encrypting network traffic", "Speeding up database queries", "Reducing memory usage"],
    "Distributed locks prevent race conditions when multiple processes modify the same resource.", ["Redis", "Google", "Uber"])

# Hard (20)
add("System Design", "hard", "In the CAP theorem, why can't a system guarantee all three properties during a network partition?",
    "During a partition, a write to one side can't reach the other — you must either reject the write (lose A) or serve stale data (lose C)", ["CAP is only theoretical", "Network partitions never actually happen", "Consistency and availability are the same thing"],
    "CAP forces a tradeoff: CP systems (like ZooKeeper) reject requests during partition; AP systems (like Cassandra) serve potentially stale data.", ["Amazon", "Google"])

add("System Design", "hard", "How does Kafka achieve exactly-once delivery semantics?",
    "Through idempotent producers, transactional writes, and consumer offset management within transactions", ["By sending every message three times", "By using TCP's built-in reliability", "By storing messages in RAM only"],
    "Exactly-once requires coordination across producers, brokers, and consumers.", ["LinkedIn", "Confluent", "Uber"])

add("System Design", "hard", "What is the Raft consensus algorithm used for?",
    "Electing a leader and replicating a log of operations across distributed nodes to achieve consensus", ["Encrypting data at rest", "Sorting distributed data", "Load balancing HTTP requests"],
    "Raft is easier to understand than Paxos and is used in etcd, CockroachDB, and Consul.", ["Google", "HashiCorp"])

add("System Design", "hard", "In a distributed system, what is a vector clock?",
    "A mechanism to track causal ordering of events across multiple nodes without a global clock", ["A real-time clock synchronized via NTP", "A timer for garbage collection", "A cron job scheduler"],
    "Each node maintains a vector of logical timestamps. Comparing vectors determines happens-before relationships.", ["Amazon", "Google"])

add("System Design", "hard", "What is the difference between SAGA and two-phase commit (2PC) for distributed transactions?",
    "2PC uses a coordinator with locking for strong consistency; SAGA uses compensating transactions for eventual consistency", ["They are the same protocol", "SAGA is always faster", "2PC doesn't require a coordinator"],
    "2PC blocks on coordinator failure; SAGA sacrifices atomicity for availability.", ["Uber", "Netflix"])

add("System Design", "hard", "How does a gossip protocol work in distributed systems?",
    "Each node periodically shares its state with a random subset of peers, and information propagates epidemically", ["A central server broadcasts to all nodes simultaneously", "Nodes only communicate with their immediate neighbors in a ring", "It requires a global lock before any communication"],
    "Gossip is used by Cassandra for failure detection and membership management.", ["Amazon", "Apple"])

add("System Design", "hard", "What is CRDTs (Conflict-free Replicated Data Types) and when would you use them?",
    "Data structures that can be replicated and merged automatically without conflicts, used for eventual consistency", ["A type of database index", "A compression algorithm", "A form of data encryption"],
    "CRDTs (like G-Counter, LWW-Register) enable offline-first applications and collaborative editing.", ["Google Docs", "Figma", "Apple"])

add("System Design", "hard", "What is the 'split brain' problem in distributed systems?",
    "When a network partition causes two parts of a cluster to independently believe they are the active leader", ["When a database table is split across two disks", "When a load balancer has two IPs", "When a microservice has two versions deployed"],
    "Split brain can cause conflicting writes. Fencing tokens and quorum-based elections prevent this.", ["Google", "Amazon"])

add("System Design", "hard", "How does Redis Cluster handle failover when a master node goes down?",
    "Replica nodes detect the failure via gossip, hold an election, and one replica is promoted to master", ["All data is lost and must be restored from backup", "The cluster stops accepting all requests", "A human operator must manually intervene"],
    "Redis Cluster uses a gossip protocol for failure detection and automatic failover.", ["Twitter", "GitHub", "Stripe"])

add("System Design", "hard", "Explain the log-structured merge tree (LSM-tree) and where it is used.",
    "Writes go to an in-memory buffer, then flush to sorted files on disk, periodically merged — optimized for write-heavy workloads", ["A tree that only stores log messages", "A B-Tree variant for read optimization", "A data structure used exclusively in DNS servers"],
    "LSM trees are used in Cassandra, LevelDB, and RocksDB.", ["Google", "Facebook", "Amazon"])

add("System Design", "hard", "What is a quorum in the context of distributed databases?",
    "The minimum number of nodes that must agree for a read/write to be considered successful (typically W + R > N)", ["All nodes must agree unanimously", "Only one node needs to respond", "It refers to the maximum cluster size"],
    "Quorum ensures overlap between read and write sets, guaranteeing consistency.", ["Amazon", "Google"])

add("System Design", "hard", "What is tail latency and why does it matter (p99 vs p50)?",
    "Tail latency (p99) measures the slowest 1% of requests — it affects user experience disproportionately in large-scale systems", ["Tail latency is the fastest response time", "p99 is always equal to p50", "It only matters for batch processing"],
    "A 1% slow path may affect 50%+ of end-to-end requests when fanout is high.", ["Google", "Amazon"])

add("System Design", "hard", "What is the Paxos consensus algorithm's core mechanism?",
    "A proposer sends a proposal number; acceptors promise not to accept lower-numbered proposals; a majority forms consensus", ["Nodes vote on the fastest responder", "A central coordinator assigns values", "A random node is selected as leader"],
    "Paxos guarantees safety but can live-lock without a distinguished proposer.", ["Google", "Microsoft"])

add("System Design", "hard", "What is the difference between push-based and pull-based monitoring?",
    "Push: services send metrics to a collector (e.g., StatsD); Pull: collector scrapes services at intervals (e.g., Prometheus)", ["There is no difference", "Push is always better", "Pull requires no network access"],
    "Pull-based can detect if a service is down (scrape fails); push-based can handle dynamic/ephemeral services.", ["Google", "Datadog"])

add("System Design", "hard", "How does Amazon DynamoDB handle hot partition keys?",
    "Adaptive capacity automatically redistributes throughput from less-active partitions to hot partitions", ["It duplicates the data across all partitions", "It rejects all writes to hot keys", "It doesn't handle hot keys at all"],
    "DynamoDB also supports write sharding patterns (adding random suffixes to keys).", ["Amazon"])

add("System Design", "hard", "In microservices, what is the outbox pattern?",
    "Writing events to a local 'outbox' table in the same DB transaction, then asynchronously publishing them to a message broker", ["A pattern for storing user emails", "A caching strategy", "A method for deleting old logs"],
    "The outbox pattern solves the dual-write problem — ensuring data and events are consistent.", ["Uber", "Netflix"])

add("System Design", "hard", "What is multi-tenancy and what are its architectural tradeoffs?",
    "Serving multiple customers from one shared application instance; trades isolation for cost efficiency", ["Each customer gets their own data center", "Data is never shared between any users", "It requires dedicated hardware per tenant"],
    "Schema-per-tenant offers isolation; shared-schema offers efficiency. Row-level security is a middle ground.", ["Salesforce", "Shopify"])

add("System Design", "hard", "What is the purpose of consistent prefix reads in distributed databases?",
    "Ensuring reads respect causal ordering so a reader never sees an effect without its cause", ["Reading the most recent write always", "Reading from a specific partition only", "Ensuring alphabetical ordering of results"],
    "Without consistent prefix, you might see a reply to a message before the original message.", ["Microsoft", "Google"])

add("System Design", "hard", "How does a content-addressable storage (CAS) system work?",
    "Data is stored and retrieved using a hash of its content as the key, enabling deduplication", ["Data is stored by user ID", "Content is always encrypted at rest", "Files are sorted alphabetically"],
    "CAS enables automatic deduplication — identical content produces the same hash/address.", ["Google", "Dropbox"])

add("System Design", "hard", "What is the Byzantine Generals Problem?",
    "Achieving consensus among distributed nodes when some nodes may be faulty or malicious", ["A database sharding strategy", "A network routing algorithm", "A caching invalidation problem"],
    "BFT protocols (like PBFT) tolerate up to f Byzantine faults with 3f+1 nodes.", ["Google", "Blockchain"])


# =============================================================================
#  Computer Networks — 60 questions
# =============================================================================

# Easy (20)
add("CN", "easy", "What does DNS stand for?",
    "Domain Name System", ["Data Network Service", "Digital Naming Standard", "Direct Node Switching"],
    "DNS translates human-readable domain names (like google.com) to IP addresses.", ["Cloudflare", "Google"])

add("CN", "easy", "Which protocol is connection-oriented: TCP or UDP?",
    "TCP", ["UDP", "Both", "Neither"],
    "TCP establishes a connection via a three-way handshake before data transfer.")

add("CN", "easy", "What does HTTP status code 404 indicate?",
    "Resource not found", ["Server error", "Redirect", "Successful request"],
    "404 means the server cannot find the requested URL.")

add("CN", "easy", "What layer of the OSI model does a router operate on?",
    "Network layer (Layer 3)", ["Data Link layer (Layer 2)", "Application layer (Layer 7)", "Physical layer (Layer 1)"],
    "Routers use IP addresses at Layer 3 to forward packets between networks.", ["Cisco", "Juniper"])

add("CN", "easy", "What is an IP address?",
    "A numerical label assigned to each device on a network for identification and addressing", ["A physical hardware identifier", "A domain name", "A type of encryption key"],
    "IPv4 uses 32-bit addresses; IPv6 uses 128-bit addresses.")

add("CN", "easy", "What port does HTTP typically use?",
    "80", ["443", "22", "21"],
    "HTTP uses port 80 by default; HTTPS uses port 443.")

add("CN", "easy", "What does ARP (Address Resolution Protocol) do?",
    "Maps an IP address to a MAC (hardware) address on a local network", ["Maps a domain name to an IP address", "Encrypts network traffic", "Routes packets between networks"],
    "ARP operates at the Data Link layer to resolve IP-to-MAC within a LAN.", ["Cisco"])

add("CN", "easy", "What is the main difference between IPv4 and IPv6?",
    "IPv4 uses 32-bit addresses (~4.3 billion); IPv6 uses 128-bit addresses (virtually unlimited)", ["IPv6 is slower than IPv4", "IPv4 supports encryption but IPv6 doesn't", "IPv6 only works over Wi-Fi"],
    "IPv6 was created to address IPv4 address exhaustion.", ["AT&T", "Verizon"])

add("CN", "easy", "What is a MAC address?",
    "A unique hardware identifier assigned to a network interface card (NIC)", ["An IP address used by Mac computers", "A type of domain name", "A password for Wi-Fi"],
    "MAC addresses are 48-bit addresses used at the Data Link layer.")

add("CN", "easy", "What is a subnet mask?",
    "A 32-bit number that divides an IP address into network and host portions", ["A firewall rule", "A type of encryption", "A domain name format"],
    "For example, 255.255.255.0 (/24) means the first 24 bits identify the network.", ["Cisco"])

add("CN", "easy", "What is the purpose of DHCP?",
    "Automatically assigning IP addresses to devices on a network", ["Encrypting DNS queries", "Transferring files between servers", "Balancing network load"],
    "DHCP eliminates the need for manual IP configuration on each device.")

add("CN", "easy", "Which transport layer protocol does video streaming typically prefer?",
    "UDP", ["TCP", "ICMP", "ARP"],
    "UDP's lower overhead is preferred for real-time applications where occasional packet loss is acceptable.")

add("CN", "easy", "What is a firewall?",
    "A network security device that monitors and filters incoming/outgoing traffic based on rules", ["A type of router", "An encryption protocol", "A database system"],
    "Firewalls can be hardware-based, software-based, or cloud-based.", ["Palo Alto", "Fortinet"])

add("CN", "easy", "What does ICMP stand for and what is it used for?",
    "Internet Control Message Protocol — used for error reporting and diagnostics (e.g., ping)", ["Internet Connection Management Protocol — manages TCP connections", "Internal Cache Memory Protocol — manages CPU cache", "Integrated Circuit Monitoring Platform — monitors hardware"],
    "The 'ping' command uses ICMP Echo Request/Reply messages.")

add("CN", "easy", "What is a VLAN?",
    "A Virtual LAN that logically segments a physical network into separate broadcast domains", ["A type of VPN", "A wireless network standard", "A video streaming protocol"],
    "VLANs improve security and reduce broadcast traffic without requiring physical separation.", ["Cisco", "Juniper"])

add("CN", "easy", "What is the three-way handshake in TCP?",
    "SYN → SYN-ACK → ACK", ["FIN → ACK → RST", "GET → POST → PUT", "HELLO → OK → BYE"],
    "Client sends SYN, server responds with SYN-ACK, client confirms with ACK.")

add("CN", "easy", "What is NAT (Network Address Translation)?",
    "A technique that remaps private IP addresses to a public IP for outbound internet traffic", ["A new type of IP address", "A DNS configuration method", "A data encryption standard"],
    "NAT allows multiple devices on a private network to share a single public IP.", ["Cisco"])

add("CN", "easy", "What does HTTPS add over HTTP?",
    "TLS/SSL encryption for secure data transmission", ["Faster download speeds", "Larger file support", "Support for video streaming"],
    "HTTPS encrypts data in transit, preventing eavesdropping and tampering.")

add("CN", "easy", "What is a default gateway?",
    "The router's IP address that a device uses to send traffic outside its local network", ["The fastest server on the network", "The DNS server address", "The MAC address of the switch"],
    "Without a default gateway, a device can only communicate within its own subnet.")

add("CN", "easy", "What is the difference between a hub and a switch?",
    "A hub broadcasts to all ports; a switch forwards frames only to the destination MAC address", ["They are identical devices", "A switch broadcasts; a hub is selective", "A hub works at Layer 3; a switch at Layer 1"],
    "Switches are smarter and more efficient, reducing unnecessary network traffic.", ["Cisco"])

# Medium (20)
add("CN", "medium", "What happens during TCP congestion control when three duplicate ACKs are received?",
    "Fast Retransmit is triggered: the lost segment is resent and the congestion window is halved (Fast Recovery)", ["The connection is terminated with RST", "The congestion window drops to 1 MSS (Slow Start)", "The sender doubles its window size"],
    "3 duplicate ACKs indicate a single packet loss, not severe congestion, so the response is less aggressive than a timeout.", ["Cisco", "Akamai", "Cloudflare"])

add("CN", "medium", "How many usable host addresses does a /28 subnet have?",
    "14 (16 total minus network and broadcast addresses)", ["16", "30", "256"],
    "A /28 mask leaves 4 host bits: 2^4 = 16 total, minus 2 reserved = 14 usable.", ["Cisco", "Juniper"])

add("CN", "medium", "What is the Store-and-Forward delay (transmission delay) of a packet?",
    "Packet length (L bits) divided by the link transmission rate (R bits/sec), i.e., L/R", ["The speed of light across the fiber", "The time to encrypt the packet", "The time to perform DNS lookup"],
    "It's the time for the router to receive all bits before forwarding. Distinct from propagation delay.", ["Cisco"])

add("CN", "medium", "What is the difference between symmetric and asymmetric encryption?",
    "Symmetric uses one shared key for both encryption/decryption; asymmetric uses a public-private key pair", ["Symmetric is slower than asymmetric", "Asymmetric uses the same key for both", "There is no meaningful difference"],
    "HTTPS uses asymmetric encryption to exchange a symmetric session key (TLS handshake).", ["Cloudflare"])

add("CN", "medium", "What is BGP (Border Gateway Protocol) used for?",
    "Routing traffic between autonomous systems (AS) on the internet", ["Encrypting email", "Resolving domain names", "Managing DHCP leases"],
    "BGP is the protocol that makes the global internet routing table work.", ["Cisco", "AWS", "Google"])

add("CN", "medium", "In TCP, what is the purpose of the sliding window mechanism?",
    "Flow control — allowing the sender to transmit multiple packets before waiting for acknowledgments", ["Sorting packets in order", "Encrypting data", "Route discovery"],
    "The window size determines how much unacknowledged data can be in-flight.", ["Cisco", "Akamai"])

add("CN", "medium", "What is a TLS handshake's primary purpose?",
    "Authenticating the server (and optionally the client) and negotiating encryption keys for the session", ["Compressing the HTTP request body", "Balancing load across servers", "Caching DNS records"],
    "The TLS handshake establishes a shared secret used for symmetric encryption of the session.", ["Cloudflare", "Google"])

add("CN", "medium", "What is the difference between TCP and UDP?",
    "TCP is reliable, ordered, and connection-oriented; UDP is unreliable, unordered, and connectionless", ["UDP is always faster", "TCP supports multicast but UDP doesn't", "UDP establishes connections; TCP doesn't"],
    "TCP adds overhead for reliability; UDP sacrifices reliability for lower latency.")

add("CN", "medium", "What is OSPF (Open Shortest Path First)?",
    "A link-state interior gateway protocol that uses Dijkstra's algorithm to compute shortest paths", ["An application-layer file transfer protocol", "A DNS resolution algorithm", "A type of firewall"],
    "OSPF routers exchange LSAs (Link State Advertisements) to build a complete network topology.", ["Cisco", "Juniper"])

add("CN", "medium", "What is the purpose of TTL (Time to Live) in an IP packet?",
    "Limiting the number of hops a packet can traverse, preventing infinite routing loops", ["Specifying how long a TCP connection can stay open", "Setting the encryption key expiry", "Determining maximum packet payload size"],
    "Each router decrements the TTL by 1. When it reaches 0, the packet is discarded.")

add("CN", "medium", "What is an STP (Spanning Tree Protocol)?",
    "A protocol that prevents loops in Ethernet networks by creating a loop-free logical topology", ["A process for splitting traffic across subnets", "A method for encrypting Layer 2 frames", "A way to prioritize VoIP traffic"],
    "Without STP, broadcast storms can crash the network.", ["Cisco"])

add("CN", "medium", "What is the difference between a stateful and a stateless firewall?",
    "Stateful firewalls track connection state (allowing return traffic); stateless firewalls filter each packet independently", ["Stateless are always more secure", "Stateful firewalls don't inspect packets", "There is no real difference"],
    "Stateful inspection is smarter but uses more resources.", ["Palo Alto", "Cisco"])

add("CN", "medium", "What is DNS caching and what is its risk?",
    "Storing DNS responses locally to speed up future lookups; risk is serving stale/outdated records", ["DNS caching encrypts queries", "Caching increases DNS resolution time", "DNS caching has no risks"],
    "TTL controls how long cached DNS records are valid before re-querying.", ["Cloudflare"])

add("CN", "medium", "What is the purpose of MPLS (Multi-Protocol Label Switching)?",
    "Directing traffic along predetermined paths using labels instead of IP lookups for faster forwarding", ["Encrypting VoIP calls", "Managing DHCP address pools", "Resolving DNS queries faster"],
    "MPLS adds a label to packets, enabling fast switching at each router without complex IP lookups.", ["Cisco", "Juniper"])

add("CN", "medium", "What is HTTP/2's main improvement over HTTP/1.1?",
    "Multiplexing multiple requests over a single TCP connection, eliminating head-of-line blocking at the HTTP layer", ["Using a different port number", "Removing the need for DNS", "Supporting only GET requests"],
    "HTTP/2 also uses header compression (HPACK) and server push.", ["Google", "Cloudflare"])

add("CN", "medium", "What is the maximum segment size (MSS) in TCP?",
    "The largest amount of data TCP will send in a single segment, negotiated during the handshake", ["The maximum number of simultaneous connections", "The maximum IP packet size", "The maximum number of hops"],
    "MSS is typically MTU (1500 bytes) minus TCP (20 bytes) and IP (20 bytes) headers = 1460 bytes.")

add("CN", "medium", "What is a proxy server?",
    "An intermediary that forwards requests on behalf of clients, providing anonymity, filtering, or caching", ["A primary DNS server", "A type of database", "A wireless access point"],
    "Forward proxies act for clients; reverse proxies act for servers.", ["Cloudflare"])

add("CN", "medium", "What is Quality of Service (QoS)?",
    "Mechanisms to prioritize certain types of network traffic (e.g., VoIP over file downloads)", ["A certification for network hardware", "A type of encryption", "A DNS configuration standard"],
    "QoS uses techniques like traffic shaping, queuing, and marking to manage bandwidth.", ["Cisco"])

add("CN", "medium", "What is the difference between half-duplex and full-duplex communication?",
    "Half-duplex allows communication in one direction at a time; full-duplex allows simultaneous two-way communication", ["Half-duplex is always faster", "Full-duplex uses half the bandwidth", "They are the same thing"],
    "Ethernet hubs use half-duplex; modern switches and TCP connections use full-duplex.")

add("CN", "medium", "What is an anycast address?",
    "A single IP address advertised from multiple locations; traffic is routed to the nearest instance", ["An IP address that broadcasts to all devices", "A private IP address", "A multicast group address"],
    "CDNs use anycast to direct users to the closest edge server automatically.", ["Cloudflare", "Google"])

# Hard (20)
add("CN", "hard", "How does TCP handle congestion during Slow Start?",
    "The congestion window doubles every RTT (exponential growth) until reaching ssthresh, then switches to linear growth (Congestion Avoidance)", ["The window stays constant and never changes", "Packets are sent one at a time always", "The sender waits for explicit permission from the receiver"],
    "Slow Start probes network capacity. After a timeout, cwnd resets to 1 and ssthresh is halved.", ["Cisco", "Akamai"])

add("CN", "hard", "In SDN (Software-Defined Networking), what is the role of the Southbound API (e.g., OpenFlow)?",
    "Enabling the centralized SDN controller to program the forwarding rules of network switches in the data plane", ["Allowing end-user applications to configure network policies", "Encrypting traffic between edge routers", "Managing DNS resolution for the controller"],
    "The Northbound API connects applications to the controller; Southbound connects the controller to switches.", ["VMware", "Cisco", "Juniper"])

add("CN", "hard", "What is the main difference between distance-vector and link-state routing protocols?",
    "Distance-vector (e.g., RIP) shares routing tables with neighbors periodically; link-state (e.g., OSPF) floods the entire topology and each router computes shortest paths locally", ["They are the same algorithm", "Link-state shares tables; distance-vector computes locally", "Distance-vector always converges faster"],
    "Link-state converges faster and avoids the count-to-infinity problem.", ["Cisco", "Juniper"])

add("CN", "hard", "What is QUIC protocol and what problem does it solve?",
    "A transport protocol built on UDP that provides multiplexed connections with reduced handshake latency (0-RTT), avoiding TCP's head-of-line blocking", ["A database query language", "A file compression algorithm", "An email encryption standard"],
    "QUIC (used by HTTP/3) combines transport and encryption handshakes, achieving 0-RTT connection resumption.", ["Google", "Cloudflare"])

add("CN", "hard", "Explain the count-to-infinity problem in distance-vector routing.",
    "When a link fails, routers keep incrementing the cost through each other because they rely on neighbor information, causing extremely slow convergence", ["Routers run out of memory", "The routing table overflows", "Packet TTL reaches infinity"],
    "Solutions include split horizon, poison reverse, and triggered updates.", ["Cisco"])

add("CN", "hard", "What is a TCP RST attack?",
    "An attacker sends forged RST packets to forcibly terminate an active TCP connection between two parties", ["Restarting a router remotely", "Resetting DNS caches", "Redirecting HTTP traffic"],
    "The attacker must guess the sequence number. This attack can disrupt BGP sessions.", ["Cloudflare", "Akamai"])

add("CN", "hard", "How does multipath TCP (MPTCP) work?",
    "It allows a single TCP connection to use multiple network paths simultaneously, improving throughput and resilience", ["It routes each packet on a different path independently", "It encrypts data on multiple layers", "It creates backup DNS entries"],
    "MPTCP is useful for mobile devices switching between Wi-Fi and cellular.", ["Apple", "Google"])

add("CN", "hard", "What is Segment Routing?",
    "A source routing paradigm where the source node encodes the path as an ordered list of segments (instructions) in the packet header", ["Splitting TCP segments into smaller chunks", "A DDoS mitigation technique", "A VPN tunneling protocol"],
    "Segment Routing simplifies network control planes and is used with both MPLS and IPv6.", ["Cisco", "Google"])

add("CN", "hard", "What is the purpose of ECN (Explicit Congestion Notification)?",
    "Allowing routers to signal congestion by marking packets instead of dropping them, enabling end-to-end congestion awareness without packet loss", ["Encrypting network traffic at Layer 2", "Notifying DNS servers of IP changes", "Enabling multicast routing"],
    "ECN uses 2 bits in the IP header and reduces unnecessary retransmissions.", ["Google", "Akamai"])

add("CN", "hard", "What is the MTU Path Discovery mechanism?",
    "A technique where the sender probes the path by sending packets with the Don't Fragment bit set, reducing size on ICMP 'Fragmentation Needed' responses until the path MTU is found", ["A DNS query optimization", "A routing protocol", "A bandwidth measurement tool"],
    "Path MTU Discovery prevents fragmentation, which can hurt performance.", ["Cisco"])

add("CN", "hard", "What is the Nagle algorithm and when might you disable it?",
    "It combines small TCP segments into larger ones to reduce overhead; disable it for latency-sensitive applications like gaming or interactive terminals", ["It encrypts small packets", "It fragments large packets", "It compresses HTTP headers"],
    "TCP_NODELAY socket option disables Nagle's algorithm.", ["Akamai", "Netflix"])

add("CN", "hard", "How does DNS over HTTPS (DoH) differ from traditional DNS?",
    "DoH encrypts DNS queries within HTTPS, preventing ISPs and middleboxes from seeing which domains are being resolved", ["DoH uses port 53 like traditional DNS", "DoH is faster because it skips encryption", "DoH only works with IPv6"],
    "DoH improves privacy but makes network-level content filtering harder.", ["Cloudflare", "Google", "Mozilla"])

add("CN", "hard", "What is the Leaky Bucket algorithm as used in network traffic shaping?",
    "Packets enter a fixed-capacity bucket; the bucket leaks at a constant rate, smoothing bursty traffic to a steady output", ["A method to detect packet corruption", "A DDoS attack technique", "A way to encrypt network headers"],
    "Unlike token bucket, leaky bucket enforces a strict constant output rate.")

add("CN", "hard", "What is the TCP TIME_WAIT state and why does it exist?",
    "After closing a connection, the socket stays in TIME_WAIT for 2×MSL to ensure retransmitted FIN/ACKs are handled and old segments don't corrupt new connections", ["It waits for the server to restart", "It encrypts the remaining data", "It compresses outgoing packets"],
    "TIME_WAIT can cause port exhaustion on servers with many short-lived connections.")

add("CN", "hard", "What is VXLAN and what problem does it solve?",
    "A tunneling protocol that encapsulates Layer 2 Ethernet frames in UDP, enabling large-scale network virtualization beyond VLAN's 4096 limit", ["A new version of HTML", "A database replication protocol", "A wireless security standard"],
    "VXLAN uses a 24-bit segment ID, supporting ~16 million virtual networks.", ["VMware", "Cisco"])

add("CN", "hard", "What is SD-WAN?",
    "A virtualized WAN architecture that abstracts and centrally manages connectivity across branch offices, data centers, and cloud — using any transport (MPLS, broadband, LTE)", ["A type of storage area network", "A wireless LAN technology", "A database administration tool"],
    "SD-WAN improves WAN management by decoupling the control plane from the data plane.", ["Cisco", "VMware"])

add("CN", "hard", "How does TCP Selective Acknowledgment (SACK) improve performance?",
    "It allows the receiver to acknowledge non-contiguous blocks of received data, so the sender retransmits only the missing segments instead of everything after the loss", ["It acknowledges every single byte individually", "It combines all ACKs into one packet", "It disables congestion control"],
    "Without SACK, TCP uses Go-Back-N, retransmitting all segments after a loss.", ["Akamai", "Cloudflare"])

add("CN", "hard", "What is BFD (Bidirectional Forwarding Detection)?",
    "A lightweight protocol for rapid detection of link/path failures between two forwarding engines, enabling sub-second failover", ["A backup file deletion mechanism", "A browser fingerprinting detection tool", "A DDoS mitigation protocol"],
    "BFD operates at millisecond intervals, much faster than routing protocol keepalives.", ["Cisco", "Juniper"])

add("CN", "hard", "Explain the concept of 'flow' in networking and how NetFlow works.",
    "A flow is a sequence of packets sharing source/destination IP, ports, and protocol. NetFlow exports flow data to a collector for traffic analysis and monitoring.", ["A flow is a single TCP packet", "NetFlow is a type of firewall", "Flows are only used in wireless networks"],
    "NetFlow helps identify top talkers, detect anomalies, and plan capacity.", ["Cisco"])

add("CN", "hard", "What is the difference between eBGP and iBGP?",
    "eBGP runs between different Autonomous Systems; iBGP runs within a single AS. iBGP requires a full mesh or route reflectors to propagate routes.", ["eBGP is faster", "iBGP uses UDP", "They use different port numbers"],
    "eBGP modifies the next-hop attribute; iBGP does not by default.", ["Cisco", "Google", "AWS"])


# =============================================================================
#  OOPS — 50 questions
# =============================================================================

# Easy (17)
add("OOPS", "easy", "What is a class in OOP?",
    "A blueprint for creating objects that defines properties (fields) and behaviors (methods)", ["A compiled binary file", "A type of database", "A network protocol"],
    "Classes are templates; objects are instances of classes.")

add("OOPS", "easy", "What is encapsulation?",
    "Bundling data and methods together and restricting direct access to internal state", ["Making all variables global", "Inheriting from multiple classes", "Converting code to bytecode"],
    "Encapsulation hides implementation details behind a public interface (getters/setters).", ["Amazon", "Infosys"])

add("OOPS", "easy", "Inheritance models which type of relationship?",
    "is-a (a Dog is-a Animal)", ["has-a", "uses-a", "contains-a"],
    "Inheritance creates a parent-child hierarchy where the child 'is a' specialized version of the parent.")

add("OOPS", "easy", "What is polymorphism?",
    "The ability of different types to be treated through a common interface, with behavior varying at runtime", ["Having multiple constructors", "Using multiple databases", "Writing code in multiple languages"],
    "Polymorphism lets you call the same method on different objects and get different behaviors.")

add("OOPS", "easy", "What is an abstract class?",
    "A class that cannot be instantiated and may contain abstract methods that subclasses must implement", ["A class with no methods", "A class stored in memory only", "A class that runs faster"],
    "Abstract classes provide a partial implementation for subclasses to complete.", ["Microsoft", "Google"])

add("OOPS", "easy", "What is the difference between an interface and an abstract class in Java?",
    "An interface can only declare method signatures (pre-Java 8); an abstract class can have fields and partial implementations", ["There is no difference", "Interfaces are faster", "Abstract classes can't have constructors"],
    "Java 8+ allows default methods in interfaces, blurring the distinction.")

add("OOPS", "easy", "What is method overloading?",
    "Defining multiple methods with the same name but different parameter types or counts (compile-time polymorphism)", ["Overriding a parent class method", "Calling a method multiple times", "Making a method static"],
    "Overloading is resolved at compile time based on the method signature.")

add("OOPS", "easy", "What is method overriding?",
    "Redefining a parent class method in a subclass with the same signature (runtime polymorphism)", ["Having multiple methods with the same name but different parameters", "Calling a method from another class", "Creating a new method"],
    "The JVM calls the overridden method based on the actual object type at runtime.", ["Amazon", "Microsoft"])

add("OOPS", "easy", "What is a constructor?",
    "A special method called automatically when an object is created to initialize its state", ["A method that destroys objects", "A method that returns a value", "A static utility method"],
    "Constructors have the same name as the class and no return type.")

add("OOPS", "easy", "Composition models which type of relationship?",
    "has-a (a Car has-a Engine)", ["is-a", "knows-a", "extends-a"],
    "Composition creates objects by combining other objects as fields.")

add("OOPS", "easy", "What is the 'this' keyword in Java?",
    "A reference to the current object instance", ["A reference to the parent class", "A static variable", "A loop counter"],
    "'this' distinguishes instance variables from parameters with the same name.")

add("OOPS", "easy", "What is the 'super' keyword in Java?",
    "A reference to the parent (super) class, used to call parent constructors or methods", ["A keyword to make a method faster", "A type of access modifier", "A return statement"],
    "super() calls the parent constructor; super.method() calls an overridden parent method.")

add("OOPS", "easy", "What are access modifiers in Java?",
    "Keywords (public, private, protected, default) that control the visibility of classes, methods, and fields", ["Keywords that speed up code execution", "Keywords that manage memory", "Keywords that handle exceptions"],
    "private = same class only; protected = same package + subclasses; public = everywhere.")

add("OOPS", "easy", "What is an object in OOP?",
    "An instance of a class that has its own state (field values) and behavior (methods)", ["A global variable", "A type of exception", "A compilation unit"],
    "Multiple objects can be created from the same class, each with different state.")

add("OOPS", "easy", "What is the difference between static and instance methods?",
    "Static methods belong to the class and can be called without an object; instance methods require an object", ["Static methods are faster", "Instance methods can't access variables", "There is no difference"],
    "Static methods cannot access instance variables or use 'this'.")

add("OOPS", "easy", "What is a getter and setter?",
    "Methods that provide controlled read (get) and write (set) access to private fields", ["Database query methods", "Methods that sort data", "Methods that handle exceptions"],
    "Getters and setters enforce encapsulation by adding validation or transformation logic.")

add("OOPS", "easy", "Can a Java class inherit from multiple classes?",
    "No, Java supports single class inheritance only (but can implement multiple interfaces)", ["Yes, Java supports multiple inheritance of classes", "Only abstract classes can be multiply inherited", "Only final classes can be multiply inherited"],
    "This design avoids the diamond problem that exists in C++.", ["Google"])

# Medium (17)
add("OOPS", "medium", "What is the Liskov Substitution Principle (LSP)?",
    "Subtypes must be substitutable for their base types without altering program correctness", ["Classes should be open for extension but closed for modification", "A class should have only one reason to change", "Depend on abstractions, not concretions"],
    "If class B extends A, anywhere you use A, you should be able to use B without surprises.", ["Intuit", "PayPal", "Capital One"])

add("OOPS", "medium", "What is the Single Responsibility Principle (SRP)?",
    "A class should have only one reason to change — it should encapsulate exactly one responsibility", ["A class should have one constructor", "A method should have one line of code", "An interface should have one method"],
    "SRP prevents 'God classes' that do too many unrelated things.", ["Amazon", "Google"])

add("OOPS", "medium", "What is the Open/Closed Principle?",
    "Software entities should be open for extension but closed for modification", ["Classes should always be final", "Methods should never be changed", "Interfaces must not have default methods"],
    "Add functionality by extending (subclassing, composition) rather than modifying existing code.", ["Microsoft"])

add("OOPS", "medium", "What is dependency injection?",
    "Providing dependencies to an object from the outside rather than having it create them internally", ["Importing libraries", "Writing unit tests", "Deploying code to production"],
    "DI enables loose coupling and easier testing by injecting mock dependencies.", ["Google", "Netflix"])

add("OOPS", "medium", "What is the Factory Pattern?",
    "A creational pattern that delegates object creation to a factory method, decoupling the client from concrete classes", ["A pattern for creating database tables", "A pattern for sorting arrays", "A pattern for network routing"],
    "Factory pattern is used when the exact type to instantiate is determined at runtime.", ["Amazon", "Google"])

add("OOPS", "medium", "What is the Singleton Pattern?",
    "Ensuring a class has only one instance and providing a global point of access to it", ["Creating one method per class", "Having one variable per object", "Allowing only one thread per process"],
    "Common uses: database connection pool, logger, configuration manager.", ["Google", "Amazon"])

add("OOPS", "medium", "What is the Observer Pattern?",
    "A pattern where an object (subject) notifies a list of dependents (observers) automatically when its state changes", ["A debugging technique", "A database querying pattern", "A network monitoring tool"],
    "Used in event-driven systems, pub/sub, and UI frameworks (MVC).", ["Netflix", "Facebook"])

add("OOPS", "medium", "What is the Strategy Pattern?",
    "Defining a family of interchangeable algorithms and making them selectable at runtime", ["A database optimization technique", "A memory management strategy", "A network routing protocol"],
    "Instead of if-else chains, inject different strategy objects to change behavior.", ["Amazon"])

add("OOPS", "medium", "What is tight coupling and why is it bad?",
    "When classes are heavily dependent on each other's implementations, making changes ripple through the codebase", ["When two threads access the same variable", "When a class has too many methods", "When a method has too many parameters"],
    "Loose coupling via interfaces and DI makes code more modular and testable.")

add("OOPS", "medium", "What is the Decorator Pattern?",
    "Dynamically adding behavior to an object by wrapping it with another object that has the same interface", ["Adding annotations to a class", "Painting a UI component", "Encrypting object fields"],
    "Java's I/O streams (BufferedReader wrapping FileReader) use the Decorator pattern.", ["Amazon", "Google"])

add("OOPS", "medium", "What is the Template Method Pattern?",
    "Defining the skeleton of an algorithm in a base class and letting subclasses override specific steps", ["A code generation template", "A pattern for HTML templates", "A database migration pattern"],
    "The base class controls the overall flow; subclasses customize individual steps.")

add("OOPS", "medium", "Why does Java not support multiple inheritance of classes?",
    "To avoid the diamond problem — ambiguity when two parent classes have methods with the same signature", ["Because Java is interpreted", "Because Java is single-threaded", "Because Java doesn't support polymorphism"],
    "Java uses interfaces instead, which can have default methods (Java 8+).", ["Bloomberg", "Samsung"])

add("OOPS", "medium", "What is the difference between aggregation and composition?",
    "In composition, the child cannot exist without the parent (strong ownership); in aggregation, the child can exist independently", ["They are identical concepts", "Aggregation is a type of inheritance", "Composition doesn't exist in Java"],
    "Example: Room-Wall is composition (wall dies with room); Department-Professor is aggregation.", ["Microsoft"])

add("OOPS", "medium", "What is the Interface Segregation Principle?",
    "Clients should not be forced to depend on interfaces they don't use — prefer many specific interfaces over one fat interface", ["Interfaces should have at most one method", "All interfaces must be public", "Interfaces cannot extend other interfaces"],
    "ISP prevents implementing unnecessary methods just to satisfy a bloated interface.", ["PayPal", "Amazon"])

add("OOPS", "medium", "What is the Dependency Inversion Principle?",
    "High-level modules should not depend on low-level modules; both should depend on abstractions", ["Invert the order of method calls", "Reverse the inheritance hierarchy", "Deploy dependencies before running code"],
    "DIP encourages coding to interfaces rather than concrete implementations.", ["Google", "Amazon"])

add("OOPS", "medium", "What is the difference between shallow copy and deep copy?",
    "Shallow copy copies references (shared internals); deep copy recursively copies all nested objects (independent clone)", ["Shallow copy is faster and always preferred", "Deep copy only works with primitive types", "They are the same in Java"],
    "Modifying a shallow copy's mutable field also affects the original.", ["Goldman Sachs"])

add("OOPS", "medium", "What is the Adapter Pattern?",
    "A structural pattern that converts the interface of one class into another interface that clients expect", ["A pattern for adapting database schemas", "A pattern for network protocol conversion", "A pattern for file format conversion"],
    "Adapters let incompatible classes work together without modifying their source code.", ["Amazon", "Google"])

# Hard (16)
add("OOPS", "hard", "What is the diamond problem in multiple inheritance?",
    "An ambiguity when a class inherits from two classes that both inherit from a common base — which version of the shared method should be used?", ["A problem with recursive data structures", "A memory leak in object creation", "A deadlock between two threads"],
    "C++ solves it with virtual inheritance; Java avoids it by not supporting multiple class inheritance.", ["Bloomberg", "Samsung"])

add("OOPS", "hard", "Why are immutable objects thread-safe?",
    "Their state cannot change after construction, so no thread can observe a partial or inconsistent update", ["They use internal locks", "They're stored in special memory", "They run in a single thread"],
    "Java examples: String, Integer, LocalDate. No synchronization needed for read-only data.", ["Google", "Goldman Sachs"])

add("OOPS", "hard", "What is the difference between covariance and contravariance in generics?",
    "Covariant types preserve the subtyping direction (Producer extends); contravariant types reverse it (Consumer super)", ["They are identical terms", "Both only apply to arrays", "Covariance is for methods; contravariance is for fields"],
    "Java's 'extends' is covariant (read-only); 'super' is contravariant (write-only). PECS: Producer Extends, Consumer Super.", ["Google", "Jane Street"])

add("OOPS", "hard", "What is the Visitor Pattern and when would you use it?",
    "A pattern that separates algorithms from the object structure they operate on, allowing new operations without modifying the classes", ["A pattern for tracking website visitors", "A pattern for managing database sessions", "A pattern for load balancing"],
    "Visitors are useful when you need to perform many distinct operations on a class hierarchy (e.g., AST processing).", ["Google", "Microsoft"])

add("OOPS", "hard", "What is double dispatch and how does the Visitor pattern implement it?",
    "Choosing the method to call based on the runtime types of both the receiver and the argument — Visitor uses accept(visitor) + visit(concreteElement)", ["Calling a method twice", "Dispatching two threads simultaneously", "Sending two network packets"],
    "Single dispatch (default in Java) chooses methods only based on the receiver's runtime type.", ["Google"])

add("OOPS", "hard", "What is the Builder Pattern and why is it preferred over telescoping constructors?",
    "A pattern that constructs complex objects step-by-step with named methods, improving readability when many parameters exist", ["A pattern for parallel construction", "A pattern for building databases", "A pattern for compiling code"],
    "Builder avoids constructors with 10+ parameters where argument order is confusing.", ["Google", "Amazon"])

add("OOPS", "hard", "What is the Proxy Pattern?",
    "Providing a surrogate object that controls access to the real object, adding behavior like lazy loading, access control, or logging", ["A network proxy server", "A database backup mechanism", "A CSS layout pattern"],
    "Java's dynamic proxies (Proxy class) and Hibernate's lazy loading use this pattern.", ["Amazon", "Netflix"])

add("OOPS", "hard", "What is the difference between method overriding and method hiding in Java?",
    "Overriding replaces behavior based on runtime type (dynamic dispatch); hiding replaces static methods based on compile-time type", ["They are the same concept", "Hiding only works with interfaces", "Overriding only works with final methods"],
    "Static methods are hidden, not overridden — the compiler decides based on the reference type.", ["Goldman Sachs", "Microsoft"])

add("OOPS", "hard", "Explain the concept of contravariant method parameter types in OOP type theory.",
    "A method override can widen (accept a more general type) its parameter types safely — this is contravariance in method parameters", ["Narrowing parameter types in override", "Having the same types always", "Using primitive types instead of objects"],
    "Java doesn't actually support contravariant parameters (it would be an overload, not override). C# and Kotlin have limited support.", ["Google", "Jane Street"])

add("OOPS", "hard", "What is the Flyweight Pattern?",
    "Sharing common parts of object state (intrinsic state) across many objects to reduce memory usage", ["Making objects lighter by removing methods", "Compressing object serialization", "Using lightweight threads"],
    "Java's String pool and Integer cache (-128 to 127) are examples of Flyweight.", ["Amazon", "Google"])

add("OOPS", "hard", "What is the Memento Pattern?",
    "Capturing and externalizing an object's internal state so it can be restored later without violating encapsulation", ["Memorizing method signatures", "Caching database queries", "Compressing object fields"],
    "Used for undo/redo functionality. The caretaker stores mementos without knowing the state structure.", ["Microsoft"])

add("OOPS", "hard", "What is the Chain of Responsibility Pattern?",
    "Passing a request along a chain of handler objects until one of them handles it", ["A linked list data structure", "A TCP connection chain", "A database query pipeline"],
    "Used in middleware chains, logging frameworks, and servlet filters.", ["Netflix", "Amazon"])

add("OOPS", "hard", "What is SOLID and why does it matter?",
    "Five principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) that produce maintainable, flexible OOP designs", ["A database transaction property", "A type of encryption", "A network protocol"],
    "SOLID violations lead to rigid, fragile code that is hard to test and extend.", ["Google", "Amazon", "Microsoft"])

add("OOPS", "hard", "What problem does the Mediator Pattern solve?",
    "Reducing chaotic many-to-many dependencies between objects by introducing a central mediator that objects communicate through", ["Mediating between two databases", "Mediating network traffic", "Mediating thread contention"],
    "Chat rooms, air traffic control, and UI event systems use the Mediator pattern.", ["Google"])

add("OOPS", "hard", "What is the difference between value objects and entity objects in DDD?",
    "Value objects are defined by their attributes (immutable, no identity); entities are defined by their identity (mutable, tracked by ID)", ["Value objects store numbers; entities store strings", "They are the same concept", "Entities cannot have methods"],
    "Money(100, USD) is a value object; Customer(id=42) is an entity.", ["Intuit", "Amazon"])

add("OOPS", "hard", "What is the Law of Demeter (Principle of Least Knowledge)?",
    "An object should only talk to its immediate friends — avoid chaining like a.getB().getC().doSomething()", ["Objects should have minimal code", "Methods should be less than 10 lines", "Classes should have at most 3 fields"],
    "Violations create tightly coupled 'train wreck' code. Use delegation instead.", ["Google", "Netflix"])


# =============================================================================
#  OS — 50 questions
# =============================================================================

# Easy (17)
add("OS", "easy", "What is the main difference between a process and a thread?",
    "A process has its own address space; threads within a process share the same address space", ["Threads are always faster", "Processes share memory by default", "A process can only have one thread"],
    "Threads have lower overhead for context switching since they share memory.", ["Google", "Bloomberg"])

add("OS", "easy", "What is virtual memory?",
    "A memory management technique that uses disk to extend available RAM, giving each process its own address space", ["Physical RAM only", "Cloud storage", "CPU cache memory"],
    "Virtual memory allows programs larger than physical RAM to run by paging to disk.")

add("OS", "easy", "What is a deadlock?",
    "A situation where two or more processes are each waiting for a resource held by another, with no progress possible", ["A crashed process", "A memory overflow", "A slow network connection"],
    "Deadlock requires mutual exclusion, hold-and-wait, no preemption, and circular wait (all four).", ["Amazon", "Microsoft"])

add("OS", "easy", "What is a context switch?",
    "Saving the state of the currently running process/thread and loading the state of the next one to run", ["Switching between programming languages", "Changing user accounts", "Restarting the OS"],
    "Context switches have overhead: saving/restoring registers, flushing TLB, etc.", ["Google"])

add("OS", "easy", "What is the role of the kernel in an OS?",
    "The core component that manages hardware resources, memory, processes, and system calls", ["A user-facing application", "A web browser", "A text editor"],
    "The kernel runs in privileged mode with direct hardware access.")

add("OS", "easy", "What is a system call?",
    "An interface through which user-space programs request services from the kernel (e.g., read, write, fork)", ["A function call between two user programs", "A network API request", "A database query"],
    "System calls involve a transition from user mode to kernel mode.", ["Microsoft", "Google"])

add("OS", "easy", "What is a page fault?",
    "An interrupt triggered when a process accesses a virtual address that is not currently mapped to physical memory", ["A compiler error", "A network timeout", "A disk formatting error"],
    "The OS handles it by loading the required page from disk into a free frame.", ["Microsoft", "Oracle"])

add("OS", "easy", "What is the difference between user mode and kernel mode?",
    "User mode restricts access to hardware and privileged instructions; kernel mode has full access", ["User mode is faster", "Kernel mode is for networking only", "There is no difference"],
    "The CPU hardware enforces mode separation for security and stability.")

add("OS", "easy", "What does the 'fork()' system call do in Unix?",
    "Creates a new child process that is a copy of the parent process", ["Opens a file", "Terminates a process", "Sends a network packet"],
    "After fork(), parent and child execute concurrently with separate address spaces.", ["Google", "Apple"])

add("OS", "easy", "What is a semaphore?",
    "A synchronization primitive that uses a counter to control access to shared resources", ["A type of memory", "A network protocol", "A file system"],
    "Binary semaphores act like mutexes; counting semaphores allow up to N concurrent accesses.", ["Amazon", "Microsoft"])

add("OS", "easy", "What scheduling algorithm gives each process an equal time slice in round?",
    "Round Robin", ["FCFS (First Come First Served)", "Priority Scheduling", "Shortest Job First"],
    "Round Robin is fair but may have higher turnaround time for short processes.", ["Google"])

add("OS", "easy", "What is a mutex?",
    "A mutual exclusion lock that ensures only one thread can access a critical section at a time", ["A memory address", "A network port", "A file descriptor"],
    "Unlike semaphores, mutexes have ownership — only the locking thread can unlock.", ["Amazon"])

add("OS", "easy", "What is an interrupt?",
    "A signal to the CPU that an event requires immediate attention, causing the CPU to switch to a handler", ["A compile error", "A syntax warning", "A network timeout"],
    "Interrupts can be hardware (keyboard, disk) or software (system calls, exceptions).")

add("OS", "easy", "What is demand paging?",
    "Loading pages into memory only when they are accessed, not in advance", ["Loading all pages at startup", "Deleting unused pages constantly", "Compressing pages in RAM"],
    "Demand paging reduces initial memory usage but may cause page faults.", ["Google"])

add("OS", "easy", "What is a file descriptor?",
    "An integer that uniquely identifies an open file or resource in a Unix process", ["A file name", "A disk sector number", "A directory path"],
    "stdin=0, stdout=1, stderr=2. New files get the lowest available FD number.")

add("OS", "easy", "What does the 'ls' command do in Unix/Linux?",
    "Lists files and directories in the current or specified directory", ["Creates a new file", "Deletes a directory", "Compiles code"],
    "'ls -la' shows detailed info including hidden files, permissions, and timestamps.")

add("OS", "easy", "What is a race condition?",
    "A bug where the outcome depends on the unpredictable timing of thread or process execution", ["A slow program", "A memory leak", "A type of deadlock"],
    "Race conditions occur when multiple threads access shared data without proper synchronization.", ["Google", "Amazon"])

# Medium (17)
add("OS", "medium", "What is thrashing in the context of virtual memory?",
    "A state where the system spends most of its time swapping pages in/out of disk rather than executing useful instructions", ["A type of disk fragmentation", "A CPU overheating problem", "A network congestion issue"],
    "Thrashing occurs when the working set of processes exceeds available physical memory.", ["Microsoft", "Oracle"])

add("OS", "medium", "What is the difference between preemptive and non-preemptive scheduling?",
    "Preemptive schedulers can interrupt a running process to give CPU to another; non-preemptive waits for the process to voluntarily yield", ["Preemptive is always slower", "Non-preemptive is used in modern OS", "They are the same"],
    "Modern OS kernels (Linux, Windows) use preemptive scheduling for responsiveness.", ["Google", "Amazon"])

add("OS", "medium", "What is a page table?",
    "A data structure used by the MMU to map virtual page numbers to physical frame numbers", ["A table of all running processes", "A list of open files", "A log of system calls"],
    "Each process has its own page table. Multi-level page tables reduce memory overhead.", ["Google", "Microsoft"])

add("OS", "medium", "What is the TLB (Translation Lookaside Buffer)?",
    "A fast cache in the CPU that stores recent virtual-to-physical address translations to speed up memory access", ["A disk buffer", "A network cache", "A process queue"],
    "TLB misses require walking the page table, which is much slower.", ["Intel", "AMD", "Google"])

add("OS", "medium", "Explain Copy-on-Write (COW) after fork().",
    "Parent and child share the same physical pages after fork(). Pages are only copied when one process tries to write to them.", ["All pages are immediately duplicated on fork()", "Pages are never copied", "Only the stack is copied"],
    "COW dramatically reduces fork() overhead for processes that exec() immediately.", ["Google", "Apple"])

add("OS", "medium", "What is the difference between starvation and deadlock?",
    "In starvation, a process waits indefinitely because others keep getting priority, but the system is still making progress. In deadlock, no process can make progress.", ["They are the same thing", "Starvation is worse than deadlock", "Deadlock involves only one process"],
    "Aging (gradually increasing priority) prevents starvation.", ["Amazon"])

add("OS", "medium", "What are the four necessary conditions for deadlock (Coffman conditions)?",
    "Mutual exclusion, hold and wait, no preemption, and circular wait", ["Starvation, livelock, priority inversion, and race condition", "Paging, segmentation, fragmentation, and thrashing", "Fork, exec, wait, and exit"],
    "Breaking any one of these conditions prevents deadlock.", ["Microsoft", "Google"])

add("OS", "medium", "What is the Banker's algorithm?",
    "A deadlock avoidance algorithm that checks if granting a resource request will leave the system in a safe state", ["An algorithm for financial transactions", "A scheduling algorithm", "A memory allocation algorithm"],
    "The system only grants requests that keep it in a state where all processes can eventually finish.", ["Google"])

add("OS", "medium", "What is internal vs. external fragmentation?",
    "Internal: wasted space within allocated blocks. External: enough total free memory exists but it's not contiguous.", ["Internal is worse than external", "External only happens in RAM", "They are the same thing"],
    "Paging eliminates external fragmentation; variable-sized allocation can cause external fragmentation.")

add("OS", "medium", "What is a zombie process?",
    "A process that has finished execution but still has an entry in the process table because its parent hasn't called wait()", ["A process that runs forever", "A process that uses no memory", "A process with root privileges"],
    "Zombies consume PID entries. Too many can exhaust the PID space.", ["Google", "Netflix"])

add("OS", "medium", "What is an orphan process?",
    "A child process whose parent has terminated. The init process (PID 1) adopts it.", ["A process with no threads", "A process with no memory", "A process that can't be killed"],
    "Orphans are handled gracefully by the OS, unlike zombies which need parent cleanup.")

add("OS", "medium", "What is the Least Recently Used (LRU) page replacement algorithm?",
    "Evicts the page that hasn't been accessed for the longest time", ["Evicts a random page", "Evicts the most recently used page", "Evicts the largest page"],
    "LRU approximates optimal replacement but requires tracking access history.", ["Google", "Amazon"])

add("OS", "medium", "What is the difference between a monolithic kernel and a microkernel?",
    "Monolithic: all OS services run in kernel space. Microkernel: only essential services (IPC, scheduling) run in kernel space; others run in user space.", ["Microkernels are always faster", "Monolithic kernels can't be compiled", "They are identical"],
    "Linux is monolithic; Minix/QNX are microkernels. Microkernels are more modular but have IPC overhead.")

add("OS", "medium", "What is priority inversion and how is it solved?",
    "A high-priority task waits for a low-priority task holding a shared resource, while medium-priority tasks preempt the low one. Solved with priority inheritance.", ["High-priority tasks always run first", "It only occurs in single-threaded systems", "It cannot be solved"],
    "In priority inheritance, the low-priority task temporarily inherits the high-priority task's priority.", ["Google", "SpaceX"])

add("OS", "medium", "What is a spinlock and when should you use it?",
    "A lock where the thread loops (spins) checking the lock instead of sleeping. Use it for very short critical sections where context-switch overhead exceeds spinning cost.", ["A lock that prevents context switches", "A lock for network resources", "A lock that spins up new threads"],
    "Spinlocks are common in kernel code and on multi-core systems.", ["Amazon", "Google"])

add("OS", "medium", "What is the 'working set' of a process?",
    "The set of pages a process is actively using during a recent time window", ["All pages ever accessed by the process", "The total RAM available", "The process's binary on disk"],
    "Keeping the working set in memory prevents thrashing.", ["Microsoft"])

add("OS", "medium", "What is memory-mapped I/O?",
    "Mapping device registers or file contents to virtual memory addresses so they can be accessed using load/store instructions", ["Mounting a USB drive", "Formatting a disk", "Compressing files in memory"],
    "mmap() in Unix maps files into a process's address space for efficient I/O.", ["Google", "Apple"])

# Hard (16)
add("OS", "hard", "What is the difference between a hard link and a symbolic (soft) link in Unix?",
    "A hard link points directly to the file's inode; a symlink contains the path to the target file. Hard links can't cross filesystems.", ["Hard links are always faster", "Symlinks use more disk space", "They are the same thing"],
    "Deleting the original file breaks a symlink but not a hard link (the inode persists).", ["RedHat", "Apple"])

add("OS", "hard", "What is the purpose of the OOM Killer in Linux?",
    "When the system is critically low on memory, the OOM Killer selects and kills a process to free memory and prevent a system crash", ["It kills all running processes", "It only logs warnings", "It adds more swap space"],
    "The OOM Killer uses a scoring heuristic (oom_score) based on memory usage and process importance.", ["Google", "Netflix"])

add("OS", "hard", "Explain the difference between user-level threads and kernel-level threads.",
    "User-level threads are managed by the application (faster context switch but can't use multiple cores); kernel threads are managed by the OS (can run on different cores but heavier)", ["They are identical", "Kernel threads are always faster", "User threads don't exist anymore"],
    "Many-to-one mapping blocks the entire process on one thread's I/O. One-to-one (Linux pthreads) avoids this.", ["Google", "Microsoft"])

add("OS", "hard", "What is the compare-and-swap (CAS) instruction?",
    "An atomic CPU instruction that compares a memory location's value with an expected value and swaps it only if they match", ["A method for comparing file sizes", "A way to swap two processes", "A type of system call"],
    "CAS is the foundation of lock-free data structures and atomic variables (Java's AtomicInteger).", ["Google", "Amazon"])

add("OS", "hard", "What is the difference between paging and segmentation?",
    "Paging divides memory into fixed-size pages; segmentation divides it into variable-size logical segments (code, data, stack)", ["They are identical", "Paging is software-based; segmentation is hardware-based", "Segmentation uses fixed-size units"],
    "Modern OS (x86-64 Linux) primarily uses paging. Segmentation provides logical memory protection.", ["Intel", "AMD"])

add("OS", "hard", "What is an inode in a Unix file system?",
    "A data structure that stores metadata about a file (permissions, size, timestamps, data block pointers) but not the file name", ["A type of network node", "A CPU instruction", "A process identifier"],
    "File names are stored in directory entries that map names to inode numbers.", ["Google", "Apple"])

add("OS", "hard", "What is the difference between blocking I/O, non-blocking I/O, and asynchronous I/O?",
    "Blocking waits until I/O completes. Non-blocking returns immediately (caller must poll). Async initiates I/O and is notified via callback when done.", ["They all wait for I/O", "Async is the same as non-blocking", "Blocking is always preferred"],
    "epoll (Linux) and kqueue (BSD) efficiently multiplex many non-blocking I/O operations.", ["Google", "Netflix"])

add("OS", "hard", "What is a futex in Linux?",
    "A fast userspace mutex — locking is handled entirely in userspace when uncontested, only entering kernel on contention", ["A file system type", "A network buffer", "A CPU register"],
    "Futexes minimize system call overhead for the common case of no contention.", ["Google"])

add("OS", "hard", "What is the slab allocator in the Linux kernel?",
    "A memory allocator that pre-allocates pools of fixed-size objects to reduce fragmentation and allocation overhead for frequently created/destroyed kernel objects", ["A disk defragmentation tool", "A process scheduler", "A network packet buffer"],
    "The slab allocator caches recently freed objects for reuse (e.g., task_struct, inode).", ["Google", "RedHat"])

add("OS", "hard", "What is RCU (Read-Copy-Update) in the Linux kernel?",
    "A synchronization mechanism that allows readers to access data without locks while writers create copies and atomically swap pointers after all readers finish", ["A file system type", "A backup strategy", "A compiler optimization"],
    "RCU is ideal for read-heavy workloads in the kernel (routing tables, file systems).", ["Google", "Meta"])

add("OS", "hard", "What is the purpose of the 'cgroups' feature in Linux?",
    "Limiting, isolating, and accounting for resource usage (CPU, memory, I/O) of process groups", ["Creating user groups", "Managing file permissions", "Encrypting processes"],
    "cgroups are fundamental to container runtimes (Docker, Kubernetes).", ["Google", "Docker"])

add("OS", "hard", "What is the difference between a signal and an interrupt?",
    "Signals are software notifications delivered to processes (e.g., SIGKILL, SIGTERM). Interrupts are hardware/CPU events that invoke kernel handlers.", ["They are identical", "Signals are faster", "Interrupts are for user-space only"],
    "Signals are asynchronous process-to-process communication; interrupts are hardware-to-kernel.", ["Google", "Apple"])

add("OS", "hard", "What is ASLR (Address Space Layout Randomization)?",
    "A security technique that randomizes the memory addresses of stack, heap, and libraries to make exploits harder", ["A type of scheduling algorithm", "A disk encryption method", "A network routing protocol"],
    "ASLR makes buffer overflow attacks harder because attackers can't predict memory layout.", ["Microsoft", "Google"])

add("OS", "hard", "What is the 'thundering herd' problem in the context of OS synchronization?",
    "When many blocked threads/processes are woken up simultaneously to compete for a single resource, causing most to immediately block again — wasting CPU", ["Too many threads causing a deadlock", "A single thread consuming all CPU", "A memory corruption issue"],
    "Solutions: use accept4() with SOCK_CLOEXEC, or use EPOLLEXCLUSIVE.", ["Netflix", "Cloudflare"])

add("OS", "hard", "Explain the ELF format and its role in Linux.",
    "Executable and Linkable Format — the standard binary format for executables, shared libraries, and object files in Linux", ["An encryption library format", "A network protocol", "A database file format"],
    "ELF files contain headers, program segments, and section tables used by the loader and linker.", ["Google", "RedHat"])

add("OS", "hard", "What is kernel bypass and DPDK?",
    "Techniques that allow applications to directly access network hardware (NICs) from userspace, bypassing the kernel network stack for ultra-low latency", ["A kernel debugging tool", "A process scheduling method", "A file system type"],
    "DPDK (Data Plane Development Kit) is widely used in high-frequency trading and network appliances.", ["Intel", "Cisco", "Jane Street"])


# =============================================================================
#  Java — 50 questions
# =============================================================================

# Easy (17)
add("Java", "easy", "What happens if you use a local variable in Java before initializing it?",
    "Compilation error — local variables must be explicitly initialized before use", ["It defaults to 0", "It defaults to null", "A runtime exception is thrown"],
    "Unlike instance variables, Java does not auto-initialize local variables.", ["Amazon", "JP Morgan"])

add("Java", "easy", "What is the difference between '==' and '.equals()' for Strings in Java?",
    "'==' compares references (memory addresses); .equals() compares the actual character content", ["They are identical for Strings", "'==' is always preferred", ".equals() compares references"],
    "String literals are pooled, so '==' may return true, but it's unreliable for non-literals.", ["Goldman Sachs"])

add("Java", "easy", "Is Java pass-by-value or pass-by-reference?",
    "Always pass-by-value — for objects, the value of the reference (pointer) is passed, not the object itself", ["Pass-by-reference for objects", "Pass-by-reference for arrays", "It depends on the type"],
    "Reassigning a parameter inside a method doesn't affect the caller's variable.", ["Google", "Amazon"])

add("Java", "easy", "What is the difference between ArrayList and LinkedList?",
    "ArrayList uses a dynamic array (fast random access O(1)); LinkedList uses a doubly linked list (fast insert/delete at ends O(1))", ["They are identical", "LinkedList is always faster", "ArrayList can't grow in size"],
    "ArrayList has better cache locality and is preferred in most real-world use cases.", ["Microsoft", "Amazon"])

add("Java", "easy", "What is autoboxing in Java?",
    "Automatic conversion between primitive types (int) and their wrapper classes (Integer)", ["Converting objects to strings", "Automatic garbage collection", "Compiling code automatically"],
    "Autoboxing can cause subtle performance issues in tight loops.", ["Goldman Sachs", "Barclays"])

add("Java", "easy", "What does the 'final' keyword do in Java?",
    "Final variable = constant, final method = can't be overridden, final class = can't be subclassed", ["Makes code run faster", "Makes variables global", "Makes methods static"],
    "String class is final, preventing inheritance.", ["Amazon"])

add("Java", "easy", "What is the difference between checked and unchecked exceptions?",
    "Checked exceptions must be caught or declared (compile-time); unchecked exceptions (RuntimeException) don't have to be", ["Checked are faster", "Unchecked must always be caught", "There is no difference in Java"],
    "IOException is checked; NullPointerException is unchecked.", ["Google", "Microsoft"])

add("Java", "easy", "What is a HashMap in Java?",
    "A hash table implementation of the Map interface that stores key-value pairs with O(1) average lookup", ["A sorted collection", "A thread-safe queue", "A linked list"],
    "HashMap allows one null key and multiple null values. Not thread-safe.", ["Amazon", "Google"])

add("Java", "easy", "What is the difference between 'abstract' and 'interface' in modern Java?",
    "Abstract classes can have state (fields) and constructors; interfaces (since Java 8) can have default methods but no state", ["Interfaces are faster", "Abstract classes can't have methods", "They are identical since Java 8"],
    "Choose interface for defining a contract; abstract class for sharing code among related classes.")

add("Java", "easy", "What keyword is used to prevent a class from being inherited?",
    "final", ["static", "private", "abstract"],
    "The String class in Java is declared final.", ["Infosys", "TCS"])

add("Java", "easy", "What is the purpose of the 'static' keyword?",
    "Declares members that belong to the class itself rather than to instances — shared across all objects", ["Makes variables immutable", "Makes methods faster", "Enables multi-threading"],
    "Static methods can be called without creating an object. They can't access instance variables.")

add("Java", "easy", "What is garbage collection in Java?",
    "Automatic memory management where the JVM reclaims memory occupied by objects that are no longer reachable", ["Manual memory deallocation like C", "File cleanup on disk", "Log file rotation"],
    "The programmer doesn't call free(). The GC identifies and collects unreachable objects.")

add("Java", "easy", "What is the default value of an int instance variable in Java?",
    "0", ["null", "undefined", "Compilation error"],
    "Instance variables get default values: 0 for numbers, false for boolean, null for objects.")

add("Java", "easy", "What is a try-with-resources statement?",
    "A try block that automatically closes resources (implementing AutoCloseable) when the block exits", ["A try block that retries on failure", "A block that tries different algorithms", "A block for handling network timeouts"],
    "Eliminates the need for explicit finally blocks to close streams/connections.", ["Amazon", "Google"])

add("Java", "easy", "What is the String pool in Java?",
    "A special memory area where the JVM stores unique string literals to save memory by reusing identical strings", ["A thread pool for string operations", "A database of valid strings", "A collection of regex patterns"],
    "String literals are interned automatically; new String('hello') bypasses the pool.", ["Goldman Sachs"])

add("Java", "easy", "What is the difference between StringBuilder and StringBuffer?",
    "StringBuilder is not thread-safe (faster); StringBuffer is synchronized (thread-safe but slower)", ["They are identical", "StringBuilder is immutable", "StringBuffer is deprecated"],
    "Use StringBuilder in single-threaded contexts for better performance.", ["Amazon", "Wipro"])

add("Java", "easy", "What does 'null' mean in Java?",
    "A special literal indicating that a reference does not point to any object", ["An empty string", "The number zero", "An undefined variable"],
    "Calling methods on null throws NullPointerException.", ["TCS", "Infosys"])

# Medium (17)
add("Java", "medium", "Does ConcurrentHashMap allow null keys or values?",
    "No — neither null keys nor null values are allowed", ["Yes, both are allowed", "Only null keys are allowed", "Only null values are allowed"],
    "This avoids ambiguity in concurrent get(): is the key absent or mapped to null?", ["Goldman Sachs", "Morgan Stanley", "Google"])

add("Java", "medium", "What is the volatile keyword used for?",
    "Ensuring that reads and writes to a variable are made directly to main memory, providing visibility across threads", ["Making a variable immutable", "Locking a variable for thread safety", "Declaring a constant"],
    "Volatile guarantees visibility but NOT atomicity. i++ on a volatile is still not thread-safe.", ["Bloomberg", "Google"])

add("Java", "medium", "What happens if you call stream operations without a terminal operation?",
    "Nothing — Java Streams are lazy; intermediate operations are not executed until a terminal operation is invoked", ["The JVM throws an exception", "Results are cached in memory", "The program hangs"],
    "map(), filter(), etc. just build the pipeline. collect(), forEach(), count() trigger execution.", ["Google", "Amazon"])

add("Java", "medium", "What is the difference between Comparable and Comparator?",
    "Comparable defines natural ordering inside the class (compareTo); Comparator defines custom ordering externally (compare)", ["They are identical", "Comparable is for sorting; Comparator is for searching", "Comparator is deprecated"],
    "Comparable = 'I can compare myself'; Comparator = 'I compare two separate objects'.", ["Amazon", "Microsoft"])

add("Java", "medium", "What is the purpose of ThreadLocal in Java?",
    "Providing each thread with its own independent copy of a variable, avoiding shared-state concurrency issues", ["Sharing a variable across all threads", "Locking a thread to one CPU core", "Storing thread names"],
    "ThreadLocal variables are stored per-thread and must be cleaned up (.remove()) to prevent memory leaks.", ["Netflix", "Uber"])

add("Java", "medium", "What is a CompletableFuture?",
    "A class for composable asynchronous programming — chaining async tasks with thenApply, thenCompose, exceptionally, etc.", ["A thread-safe list", "A blocking queue", "A timer class"],
    "CompletableFuture supports non-blocking composition without nested callbacks.", ["Google", "Amazon"])

add("Java", "medium", "What is the difference between HashMap and TreeMap?",
    "HashMap uses a hash table (O(1) average, unordered); TreeMap uses a Red-Black tree (O(log n), sorted by keys)", ["TreeMap is always faster", "HashMap is sorted", "HashMap uses a linked list internally"],
    "Use TreeMap when you need keys in sorted order; HashMap for pure speed.", ["Amazon", "Bloomberg"])

add("Java", "medium", "What is type erasure in Java generics?",
    "The JVM erases generic type parameters at compile time, making List<String> and List<Integer> the same raw type at runtime", ["Generics are preserved at runtime", "Type erasure only applies to arrays", "Generics don't work in Java"],
    "This is why you can't do 'new T()' or 'instanceof List<String>' in Java.", ["Google", "Goldman Sachs"])

add("Java", "medium", "What are functional interfaces in Java?",
    "Interfaces with exactly one abstract method, usable as the target for lambda expressions (e.g., Runnable, Predicate, Function)", ["Interfaces with no methods", "Interfaces that only use primitive types", "Interfaces that can't be implemented"],
    "The @FunctionalInterface annotation enforces the single abstract method constraint.", ["Amazon", "Google"])

add("Java", "medium", "What is the difference between synchronized method and synchronized block?",
    "Synchronized method locks the entire object (or class for static); synchronized block locks a specific object, allowing finer-grained control", ["They are identical", "Synchronized blocks are slower", "Methods can't be synchronized"],
    "Synchronized blocks reduce lock contention by limiting the critical section scope.", ["Goldman Sachs", "Visa"])

add("Java", "medium", "What is the Java Memory Model (JMM)?",
    "A specification that defines how threads interact through memory — visibility, ordering, and happens-before relationships", ["The heap and stack layout", "The JVM installation directory structure", "The Java class file format"],
    "JMM guarantees that actions in thread A are visible to thread B if connected by a happens-before relationship.", ["Google", "Amazon"])

add("Java", "medium", "What is the purpose of the 'transient' keyword?",
    "Marking a field so it is excluded from Java serialization (ObjectOutputStream)", ["Making a variable temporary", "Making a variable const", "Making a variable thread-safe"],
    "Fields like password, cache, or computed values should be transient.", ["JP Morgan"])

add("Java", "medium", "What is the difference between fail-fast and fail-safe iterators?",
    "Fail-fast (ArrayList) throws ConcurrentModificationException if modified during iteration; fail-safe (CopyOnWriteArrayList) works on a clone", ["They are the same", "Fail-safe throws exceptions", "Fail-fast is thread-safe"],
    "Fail-safe iterators may not reflect the latest modifications.", ["Google", "Amazon"])

add("Java", "medium", "What is a record in Java (Java 14+)?",
    "A compact class syntax for immutable data carriers that auto-generates equals(), hashCode(), toString(), and accessors", ["A database record type", "A way to record method calls", "A logging mechanism"],
    "Records reduce boilerplate for value-holding classes.", ["Google"])

add("Java", "medium", "What is the diamond problem and how does Java handle it with default methods?",
    "When two interfaces provide conflicting default methods, the implementing class must explicitly override and resolve the conflict", ["Java ignores the conflict", "Compilation succeeds silently", "The JVM picks one randomly"],
    "The compiler forces you to choose which implementation to use.", ["Bloomberg", "Microsoft"])

add("Java", "medium", "What is the Optional class in Java?",
    "A container that may or may not contain a value — used to avoid null and NullPointerException by making absence explicit", ["A way to make variables optional in methods", "A performance optimization", "A deprecated null wrapper"],
    "Use Optional.of(), Optional.empty(), and .orElse() instead of null checks.", ["Google", "Amazon"])

add("Java", "medium", "What is a WeakReference in Java?",
    "A reference that doesn't prevent garbage collection — the object can be collected if only weak references point to it", ["A reference that is always null", "A faster reference type", "A reference to primitive types"],
    "WeakHashMap uses WeakReferences for keys — entries are removed when keys are GC'd.", ["Bloomberg", "Goldman Sachs"])

# Hard (16)
add("Java", "hard", "What is the G1 garbage collector's 'Mixed GC' phase?",
    "It collects Young generation regions and a selected set of Old generation regions to keep pause times within a configured target", ["It only collects the Young generation", "It does a full compaction of the entire heap", "It runs in the background without any pause"],
    "G1 prioritizes Old regions with the most garbage ('garbage first').", ["Uber", "Netflix"])

add("Java", "hard", "What happens internally when a HashMap exceeds its load factor?",
    "It doubles the bucket array size and rehashes all entries to new positions (resize and rehash)", ["It throws an exception", "It starts using a linked list globally", "It compresses existing entries"],
    "Since Java 8, buckets with 8+ collisions treeify to Red-Black trees for O(log n) worst case.", ["Amazon", "Google"])

add("Java", "hard", "What is the 'happens-before' relationship in the JMM?",
    "If action A happens-before action B, then A's effects are guaranteed to be visible to B — it defines the memory visibility guarantees", ["A is always faster than B", "A and B run in different JVMs", "A and B share the same lock"],
    "Examples: unlock happens-before lock; volatile write happens-before volatile read.", ["Google", "Goldman Sachs"])

add("Java", "hard", "What is a PhantomReference and when would you use it?",
    "A reference that is enqueued in a ReferenceQueue after the object is finalized but before its memory is reclaimed — used for cleanup without finalize()", ["A reference that is always null", "A reference to phantom classes", "A volatile reference wrapper"],
    "PhantomReferences are preferred over finalize() for resource cleanup (e.g., direct ByteBuffers).", ["Google", "Netflix"])

add("Java", "hard", "What is class loading in the JVM and what is the delegation model?",
    "Classes are loaded by a hierarchy of ClassLoaders. Each loader delegates to its parent first (Bootstrap → Extension → Application). This prevents duplicate class loading.", ["Classes are loaded from disk at compile time", "All classes are loaded at startup", "Classes are loaded randomly"],
    "Custom ClassLoaders enable hot-reloading, module isolation, and plugin systems.", ["Google", "Oracle"])

add("Java", "hard", "What is the difference between ReentrantLock and synchronized?",
    "ReentrantLock offers tryLock(), timed waits, fairness options, and multiple conditions — synchronized is simpler but less flexible", ["They are identical", "synchronized is always preferred", "ReentrantLock can't be used with try-finally"],
    "ReentrantLock must be explicitly locked/unlocked in try-finally blocks.", ["Goldman Sachs", "Morgan Stanley"])

add("Java", "hard", "What is the ForkJoinPool and how does work-stealing work?",
    "A thread pool optimized for divide-and-conquer tasks. Idle threads steal tasks from the tail of busy threads' deques to maximize utilization.", ["Threads steal CPU time from each other", "It's a single-threaded executor", "Work is always distributed evenly"],
    "Java's parallel streams use ForkJoinPool.commonPool() internally.", ["Google", "Amazon"])

add("Java", "hard", "What is JIT (Just-In-Time) compilation in the JVM?",
    "The JVM compiles hot bytecode methods to native machine code at runtime for faster execution, using C1 (client) and C2 (server) compilers", ["Source code is compiled once to bytecode and never optimized", "JIT compiles all methods at startup", "JIT is a garbage collection technique"],
    "JIT enables optimizations like inlining, escape analysis, and loop unrolling.", ["Google", "Oracle"])

add("Java", "hard", "What is escape analysis in the JVM?",
    "An optimization where the JVM determines if an object is used only within a method, enabling stack allocation or lock elimination", ["Analyzing exception escaping try blocks", "Detecting memory leaks", "A security pattern"],
    "If an object doesn't 'escape' the method, it can be allocated on the stack (no GC overhead).", ["Google"])

add("Java", "hard", "What are sealed classes (Java 17)?",
    "Classes that restrict which other classes can extend or implement them, using the 'permits' keyword", ["Classes that can't have methods", "Classes stored in sealed JAR files", "Classes that are always final"],
    "Sealed classes enable exhaustive pattern matching in switch expressions.", ["Google", "Oracle"])

add("Java", "hard", "What is Metaspace and how does it differ from PermGen?",
    "Metaspace (Java 8+) stores class metadata in native memory (auto-grows) instead of a fixed-size JVM heap area (PermGen)", ["Metaspace is a type of heap", "PermGen is still used in Java 17", "They are identical"],
    "PermGen caused OutOfMemoryError with too many classes; Metaspace grows using native memory.", ["Oracle", "Netflix"])

add("Java", "hard", "What is the Unsafe class in Java?",
    "A sun.misc.Unsafe class providing low-level operations like direct memory access, CAS operations, and object creation without constructors", ["A class for unsafe type casting", "A deprecated security class", "A class that makes code slower"],
    "Unsafe is used internally by concurrent utilities (AtomicInteger) and high-performance libraries.", ["Google", "Netflix"])

add("Java", "hard", "What is Project Loom (virtual threads) in Java?",
    "Lightweight, JVM-managed threads that can run millions concurrently without the overhead of OS threads — ideal for I/O-bound workloads", ["A new garbage collector", "A build tool", "A networking library"],
    "Virtual threads (Java 21) decouple threads from OS threads using continuation-based scheduling.", ["Oracle", "Google", "Netflix"])

add("Java", "hard", "What is the difference between strong, soft, weak, and phantom references?",
    "Strong: prevents GC. Soft: collected under memory pressure. Weak: collected at next GC. Phantom: collected, enqueued for post-mortem cleanup.", ["All references are the same", "Only strong and weak exist", "Phantom references keep objects alive"],
    "SoftReference is used for caches; WeakReference for canonicalized maps; PhantomReference for cleanup.", ["Goldman Sachs", "Bloomberg"])

add("Java", "hard", "What are VarHandles (Java 9+)?",
    "A type-safe replacement for sun.misc.Unsafe's volatile/CAS operations, supporting atomic and ordered access to fields and arrays", ["A handle to local variables", "A way to create variables at runtime", "A database connection handle"],
    "VarHandles provide fine-grained memory ordering controls similar to C++ atomics.", ["Google", "Oracle"])

add("Java", "hard", "What is the Shenandoah garbage collector?",
    "A concurrent GC that performs compaction concurrently with the application, targeting ultra-low pause times independent of heap size", ["A stop-the-world GC", "A GC for small heaps only", "A deprecated GC from Java 6"],
    "Shenandoah uses Brooks pointers to redirect references during concurrent compaction.", ["RedHat", "Amazon"])


# =============================================================================
#  Data Engineering / Dataframes — 25 questions
# =============================================================================

add("Data Engineering", "easy", "What is the key difference between a DataFrame and an RDD in Spark?",
    "DataFrames have a schema (named columns with types) and benefit from Spark's Catalyst optimizer; RDDs are unstructured", ["They are identical", "RDDs are always faster", "DataFrames can't handle structured data"],
    "DataFrames enable SQL-like operations and automatic query optimization.", ["Databricks", "Amazon"])

add("Data Engineering", "easy", "What is the purpose of partitioning in Spark?",
    "Distributing data across nodes for parallel processing", ["Encrypting data", "Compressing files", "Backing up data"],
    "More partitions = more parallelism, but too many causes scheduling overhead.", ["Databricks"])

add("Data Engineering", "easy", "What is lazy evaluation in Spark?",
    "Transformations are not executed until an action (like collect or count) is called", ["All operations execute immediately", "Only filter operations are lazy", "Spark doesn't support lazy evaluation"],
    "Lazy evaluation enables Spark's optimizer to plan the most efficient execution.", ["Databricks", "Snowflake"])

add("Data Engineering", "easy", "What is the difference between map() and flatMap()?",
    "map() transforms each element to one output; flatMap() transforms each element to zero or more outputs (flattens)", ["They are identical", "flatMap() only works on strings", "map() flattens results"],
    "flatMap('hello' → ['h','e','l','l','o']) produces individual characters from strings.", ["Google", "Amazon"])

add("Data Engineering", "easy", "What is ETL?",
    "Extract, Transform, Load — a process for moving data from sources, applying transformations, and loading into a target system", ["A programming language", "A type of database", "An encryption protocol"],
    "ETL pipelines are fundamental to data warehousing and analytics.", ["Snowflake", "Databricks"])

add("Data Engineering", "medium", "What is the difference between narrow and wide transformations in Spark?",
    "Narrow transformations (map, filter) process data within a partition; wide transformations (groupBy, join) require shuffling data across partitions", ["They are identical", "Narrow requires shuffling", "Wide transformations are always faster"],
    "Shuffles are expensive — they involve disk I/O, serialization, and network transfer.", ["Databricks", "Snowflake", "Zillow"])

add("Data Engineering", "medium", "What is data skew in Spark and how does it cause problems?",
    "When data is unevenly distributed across partitions, causing some tasks to take much longer (stragglers) and potentially OOM", ["When data has spelling errors", "When data is sorted incorrectly", "When data is encrypted"],
    "One partition with 90% of data makes the entire job wait for that single slow task.", ["Uber", "Pinterest", "Databricks"])

add("Data Engineering", "medium", "What is the 'salting' technique for handling skewed joins?",
    "Adding a random integer suffix to the skewed join key, distributing the heavy key across multiple partitions", ["Adding salt to encrypt data", "Removing duplicate records", "Compressing join keys"],
    "Salting breaks up the hot key so no single partition gets overwhelmed.", ["Uber", "Pinterest"])

add("Data Engineering", "medium", "What is the difference between a data lake and a data warehouse?",
    "Data lake stores raw, unstructured data cheaply; data warehouse stores processed, structured data optimized for queries", ["They are the same thing", "Data lakes are always faster", "Data warehouses store raw data"],
    "Data lakes (S3, ADLS) + query engines (Presto, Trino) can function as a lakehouse.", ["Databricks", "Snowflake"])

add("Data Engineering", "medium", "What is Apache Parquet?",
    "A columnar storage file format optimized for analytics — enables efficient compression and column pruning", ["A row-based storage format", "A streaming protocol", "A database engine"],
    "Parquet stores data by column, so reading specific columns doesn't require scanning the entire file.", ["Databricks", "Google"])

add("Data Engineering", "medium", "What is a broadcast join in Spark?",
    "When the smaller table is small enough to fit in memory, Spark sends it to all executors to avoid an expensive shuffle", ["Joining data from a TV broadcast", "A join that uses UDP multicast", "A join that broadcasts results to a dashboard"],
    "Spark auto-broadcasts tables under spark.sql.autoBroadcastJoinThreshold (default 10MB).", ["Databricks", "Amazon"])

add("Data Engineering", "medium", "What is data lineage?",
    "Tracking the origin, movement, and transformation of data through a pipeline from source to destination", ["The number of lines in a file", "A type of database index", "An encryption chain"],
    "Data lineage helps with debugging, compliance, and impact analysis.", ["Databricks", "Google"])

add("Data Engineering", "medium", "What is the difference between batch processing and stream processing?",
    "Batch processes large volumes of data at scheduled intervals; stream processes data continuously in real-time as it arrives", ["They are identical", "Batch is always faster", "Stream processing can't handle large data"],
    "Batch: Spark, MapReduce. Stream: Kafka Streams, Flink, Spark Streaming.", ["Google", "Netflix"])

add("Data Engineering", "medium", "What is schema-on-read vs schema-on-write?",
    "Schema-on-write enforces structure at write time (RDBMS); schema-on-read applies structure at query time (data lake)", ["They are the same", "Schema-on-read is slower always", "Schema-on-write is flexible"],
    "Schema-on-read allows storing raw data and interpreting it differently for different use cases.", ["Databricks"])

add("Data Engineering", "medium", "What is a Delta Lake?",
    "An open-source storage layer that adds ACID transactions, schema enforcement, and time travel to data lakes", ["A physical lake used for data centers", "A type of NoSQL database", "A message queue"],
    "Delta Lake enables reliable data pipelines on object storage (S3, ADLS).", ["Databricks"])

add("Data Engineering", "hard", "How does Spark's Catalyst optimizer work?",
    "It converts logical query plans through analysis, optimization (predicate pushdown, column pruning), and physical planning before code generation", ["It uses AI to optimize queries", "It doesn't optimize queries", "It optimizes network traffic"],
    "Catalyst enables both rule-based and cost-based optimizations.", ["Databricks", "Google"])

add("Data Engineering", "hard", "What is exactly-once semantics in stream processing and how does Kafka Streams achieve it?",
    "Each record is processed exactly one time — Kafka Streams uses idempotent producers, transactional writes, and consumer offset management", ["It's impossible to achieve", "By processing each record three times", "By deleting duplicate records"],
    "Exactly-once requires coordination between the producer, consumer, and state store.", ["LinkedIn", "Confluent"])

add("Data Engineering", "hard", "What is the watermark concept in stream processing (e.g., Apache Flink)?",
    "A monotonically increasing timestamp that marks the boundary below which all events are assumed to have arrived — used to trigger window computations on late-arriving data", ["A digital signature on data", "A visible mark on dashboard charts", "An encryption timestamp"],
    "Late events arriving after the watermark are either dropped or sent to a side output.", ["Google", "Uber"])

add("Data Engineering", "hard", "What is the 'small files problem' in data lakes?",
    "Having millions of tiny files causes excessive metadata operations, slow listing, and poor read performance due to high per-file overhead", ["Files are too small to read", "Small files corrupt easily", "Small files use more encryption"],
    "Solutions: file compaction, coalesce/repartition in Spark, Delta Lake's OPTIMIZE.", ["Databricks", "Amazon"])

add("Data Engineering", "hard", "What is Z-ordering in Delta Lake / data layout optimization?",
    "A multi-dimensional clustering technique that co-locates related data in the same files based on multiple columns, enabling data skipping", ["Sorting data alphabetically", "Compressing files with zlib", "A type of database index"],
    "Z-ordering enables efficient queries filtering on multiple columns simultaneously.", ["Databricks"])

# =============================================================================
#  Aptitude / Math — 20 questions
# =============================================================================

add("Aptitude", "easy", "What is 20% of 150?",
    "30", ["15", "45", "20"],
    "20% = 0.20 × 150 = 30.")

add("Aptitude", "easy", "The average of 4, 8, and 12 is:",
    "8", ["10", "12", "6"],
    "(4 + 8 + 12) / 3 = 24 / 3 = 8.")

add("Aptitude", "easy", "If the ratio of A to B is 2:3 and A is 10, what is B?",
    "15", ["20", "25", "12"],
    "Each part = 10/2 = 5. B = 3 × 5 = 15.")

add("Aptitude", "easy", "A train 200m long crosses a pole in 10 seconds. What is its speed?",
    "20 m/s", ["10 m/s", "200 m/s", "2 m/s"],
    "Speed = Distance / Time = 200 / 10 = 20 m/s.")

add("Aptitude", "easy", "If a shirt costs ₹500 after a 20% discount, what was the original price?",
    "₹625", ["₹600", "₹500", "₹700"],
    "500 = 0.80 × original. Original = 500 / 0.80 = 625.")

add("Aptitude", "medium", "A can do a job in 12 days and B in 18 days. How many days if they work together?",
    "7.2 days", ["6 days", "9 days", "15 days"],
    "Combined rate = 1/12 + 1/18 = 5/36. Time = 36/5 = 7.2 days.")

add("Aptitude", "medium", "The compound interest on ₹10,000 at 10% per annum for 2 years is:",
    "₹2,100", ["₹2,000", "₹1,100", "₹2,200"],
    "CI = P(1+r)^n - P = 10000(1.1)² - 10000 = 12100 - 10000 = 2100.")

add("Aptitude", "medium", "Two pipes can fill a tank in 6 and 8 hours. A drain empties it in 12 hours. How long to fill with all three open?",
    "24/5 = 4.8 hours", ["6 hours", "3 hours", "8 hours"],
    "Net rate = 1/6 + 1/8 - 1/12 = 5/24. Time = 24/5 = 4.8 hours.")

add("Aptitude", "medium", "How many 3-digit numbers are divisible by 7?",
    "128", ["142", "130", "100"],
    "Smallest: 105 (7×15), largest: 994 (7×142). Count = 142 - 15 + 1 = 128.")

add("Aptitude", "medium", "In how many ways can 5 people sit in a row?",
    "120", ["60", "24", "720"],
    "5! = 5 × 4 × 3 × 2 × 1 = 120.")

add("Aptitude", "medium", "If log₂(x) = 5, what is x?",
    "32", ["25", "10", "64"],
    "2^5 = 32.")

add("Aptitude", "medium", "A boat goes 12 km upstream in 3 hours and 12 km downstream in 2 hours. What is the speed of the current?",
    "1 km/hr", ["2 km/hr", "3 km/hr", "0.5 km/hr"],
    "Upstream speed = 4 km/hr, downstream = 6 km/hr. Current = (6-4)/2 = 1 km/hr.")

add("Aptitude", "hard", "In a group of 100 people, 65 like tea and 45 like coffee. How many like both if everyone likes at least one?",
    "10", ["20", "0", "45"],
    "By inclusion-exclusion: Both = 65 + 45 - 100 = 10.")

add("Aptitude", "hard", "A 6-digit number is formed using digits 1-6 without repetition. What is the probability that it is divisible by 5?",
    "1/6", ["1/5", "1/3", "1/2"],
    "The last digit must be 5. Ways = 5! / 6! = 120/720 = 1/6.")

add("Aptitude", "hard", "The sum of an infinite geometric series with first term 4 and ratio 1/2 is:",
    "8", ["4", "6", "∞"],
    "S = a / (1-r) = 4 / (1 - 0.5) = 8.")

add("Aptitude", "hard", "How many distinct words can be formed from MISSISSIPPI?",
    "34,650", ["11!", "39,916,800", "1,680"],
    "11! / (4! × 4! × 2!) = 34,650 (accounting for repeated letters I, S, P).")

add("Aptitude", "hard", "A bag has 5 red and 3 blue balls. 2 are drawn without replacement. Probability both are red?",
    "5/14", ["10/28", "25/64", "1/4"],
    "P = (5/8) × (4/7) = 20/56 = 5/14.")

add("Aptitude", "hard", "If f(x) = 2x + 3 and g(x) = x² - 1, what is f(g(2))?",
    "9", ["7", "11", "5"],
    "g(2) = 4-1 = 3. f(3) = 2(3)+3 = 9.")

add("Aptitude", "medium", "What is the HCF of 36 and 48?",
    "12", ["6", "24", "8"],
    "36 = 2² × 3², 48 = 2⁴ × 3. HCF = 2² × 3 = 12.")

add("Aptitude", "easy", "What is 15% of 200?",
    "30", ["15", "20", "35"],
    "0.15 × 200 = 30.")


# =============================================================================
#  Additional questions to reach 400+
# =============================================================================

add("DSA", "easy", "What is the height of a complete binary tree with n nodes?",
    "O(log n)", ["O(n)", "O(1)", "O(n²)"],
    "A complete binary tree has all levels fully filled except possibly the last.")

add("DSA", "easy", "What is a circular queue?",
    "A queue where the last position connects back to the first, using array space efficiently", ["A queue shaped like a ring physical device", "A queue that only stores circular data", "A stack implemented using a queue"],
    "Circular queues avoid wasting space at the front of the array after dequeuing.")

add("DSA", "medium", "What is the time complexity of inserting into a Red-Black Tree?",
    "O(log n)", ["O(1)", "O(n)", "O(n log n)"],
    "Red-Black Trees maintain balance with at most O(log n) rotations and recolorings.", ["Amazon", "Google"])

add("DSA", "medium", "What is a monotonic stack?",
    "A stack that maintains elements in either strictly increasing or decreasing order", ["A stack with only one type of data", "A stack that never grows", "A stack implemented using a queue"],
    "Monotonic stacks solve 'next greater element' type problems in O(n).", ["Amazon", "Google", "Meta"])

add("DSA", "hard", "What is the time complexity of finding the LCA (Lowest Common Ancestor) using binary lifting?",
    "O(log n) per query after O(n log n) preprocessing", ["O(n) per query", "O(1) per query with no preprocessing", "O(n²)"],
    "Binary lifting precomputes 2^k-th ancestors for each node.", ["Google", "Meta"])

add("System Design", "easy", "What is the difference between monolithic and microservices architecture?",
    "Monolithic deploys everything as a single unit; microservices deploy independent services that communicate over a network", ["Monolithic is always faster", "Microservices must use the same programming language", "They are identical"],
    "Monolithic is simpler to develop initially; microservices scale better for large teams.")

add("System Design", "medium", "What is a service mesh (e.g., Istio)?",
    "An infrastructure layer that handles service-to-service communication with features like load balancing, encryption, and observability", ["A mesh network for Wi-Fi", "A database clustering method", "A front-end framework"],
    "Service meshes use sidecar proxies (like Envoy) to intercept and manage traffic.", ["Google", "Lyft"])

add("CN", "easy", "What is the purpose of a DNS resolver?",
    "Receiving DNS queries from clients and recursively querying DNS servers to resolve domain names to IP addresses", ["Encrypting DNS traffic", "Storing website content", "Managing network switches"],
    "ISPs and services like Google (8.8.8.8) and Cloudflare (1.1.1.1) run public DNS resolvers.")

add("CN", "medium", "What is the difference between unicast, multicast, and broadcast?",
    "Unicast: one-to-one. Multicast: one-to-many (specific group). Broadcast: one-to-all on the network.", ["They all mean the same thing", "Multicast is one-to-one", "Broadcast is one-to-one"],
    "Multicast is used for streaming to subscribers; broadcast floods the entire subnet.")

add("CN", "hard", "What is the purpose of DNSSEC?",
    "Adding authentication and integrity verification to DNS responses using digital signatures, preventing DNS spoofing", ["Encrypting all DNS traffic", "Replacing DNS with a new protocol", "Speeding up DNS resolution"],
    "DNSSEC signs DNS records but does NOT encrypt queries (that's DoH/DoT).", ["Cloudflare", "Google"])

add("Java", "easy", "What is the purpose of the 'break' statement?",
    "Immediately exits the enclosing loop or switch statement", ["Pauses the thread", "Breaks the connection", "Ends the program"],
    "Without break in switch cases, execution 'falls through' to subsequent cases.")

add("Java", "medium", "What is the difference between a HashSet and a TreeSet?",
    "HashSet uses hashing (O(1) add/contains, unordered); TreeSet uses a Red-Black Tree (O(log n), sorted)", ["They are identical", "TreeSet is always faster", "HashSet maintains insertion order"],
    "Use TreeSet when you need elements in sorted order.", ["Amazon"])

add("Java", "hard", "What is string deduplication in G1 GC?",
    "G1 can automatically detect String objects with the same content and make them share the same char[] array, reducing heap usage", ["Removing duplicate strings from source code", "Compressing string literals at compile time", "Deduplicating method names"],
    "Enabled with -XX:+UseStringDeduplication. Only works with G1 GC.", ["Netflix", "Amazon"])

add("OOPS", "easy", "What is late binding (dynamic dispatch)?",
    "Resolving which method to call at runtime based on the actual object type, not the reference type", ["Binding a variable to a value at compile time", "Calling methods in reverse order", "Linking libraries at startup"],
    "Java uses late binding for instance methods (overridden methods).", ["Microsoft"])

add("OOPS", "medium", "What is the Command Pattern?",
    "Encapsulating a request as an object, allowing parameterization, queuing, and undo/redo of operations", ["A pattern for command-line parsing", "A pattern for database queries", "A pattern for network requests"],
    "Each command object has an execute() method. Supports macro commands and transaction logs.", ["Amazon", "Google"])

add("OS", "easy", "What is a shell?",
    "A command-line interface that interprets user commands and interacts with the OS kernel", ["The physical casing of a computer", "A type of memory", "A graphical window"],
    "Common shells: bash, zsh, fish. The shell forks processes to execute commands.")

add("OS", "medium", "What is a daemon process?",
    "A background process that runs without a controlling terminal, typically providing system services", ["A malicious process", "A process that only runs at night", "A process that monitors user activity"],
    "Examples: httpd (web server), sshd (SSH server), cron (job scheduler).", ["Google", "Netflix"])

add("OS", "hard", "What is memory fragmentation and how does compaction help?",
    "Fragmentation is when free memory is broken into non-contiguous blocks. Compaction moves processes together to create a large contiguous free block.", ["Fragmentation makes files larger", "Compaction deletes unused files", "Fragmentation only affects SSD"],
    "Paging avoids external fragmentation by using fixed-size frames.", ["Google"])

add("Java", "medium", "What is the difference between Runnable and Callable in Java?",
    "Runnable.run() returns void and can't throw checked exceptions; Callable.call() returns a value and can throw exceptions", ["They are identical", "Runnable is newer", "Callable can't be used with thread pools"],
    "Callable is used with ExecutorService.submit() which returns a Future.", ["Amazon", "Microsoft"])

add("Java", "medium", "What is method reference in Java 8?",
    "A shorthand lambda syntax that refers to an existing method by name (e.g., String::toUpperCase instead of s -> s.toUpperCase())", ["A way to reference methods in documentation", "A pointer to a method's memory address", "A deprecated feature"],
    "Four types: static, instance, arbitrary object, and constructor references.")

add("Data Engineering", "easy", "What is the purpose of a schema in a database?",
    "Defining the structure of data — table names, column names, data types, and constraints", ["Encrypting data", "Compressing storage", "Managing user logins"],
    "Schemas enforce data integrity by specifying what data can be stored and in what format.")

add("Data Engineering", "medium", "What is a materialized view?",
    "A precomputed query result stored as a table, refreshed periodically or on demand — speeds up complex analytical queries", ["A regular view that executes on access", "A type of index", "A compressed table"],
    "Materialized views trade storage for query speed. Must be refreshed to stay current.", ["Snowflake", "Google"])

add("Data Engineering", "hard", "What is change data capture (CDC)?",
    "A technique for tracking row-level changes (inserts, updates, deletes) in a database and streaming them to downstream systems in real-time", ["A way to capture screenshots of dashboards", "A backup compression method", "A database encryption standard"],
    "CDC tools (Debezium, DMS) enable real-time data pipelines without batch ETL delays.", ["Uber", "Netflix", "Amazon"])

add("Aptitude", "easy", "What is the next number in the series: 2, 6, 12, 20, 30, ?",
    "42", ["36", "40", "44"],
    "Differences are 4, 6, 8, 10, 12 — each increasing by 2.")

add("Aptitude", "medium", "A clock shows 3:15. What is the angle between the hour and minute hands?",
    "7.5°", ["0°", "15°", "22.5°"],
    "At 3:15, minute hand is at 90° and hour hand is at 90° + 7.5° = 97.5°. Difference = 7.5°.")

add("Aptitude", "hard", "In how many ways can 8 people be seated around a circular table?",
    "5040", ["40320", "720", "362880"],
    "Circular permutations = (n-1)! = 7! = 5040.")

add("System Design", "hard", "What is database connection multiplexing (e.g., PgBouncer)?",
    "Sharing a small pool of actual database connections among many client connections, reducing the connection overhead on the database server", ["Creating a new connection per query", "Encrypting all database connections", "Splitting queries across multiple databases"],
    "PgBouncer can handle thousands of client connections with a much smaller pool of PostgreSQL connections.", ["Uber", "Shopify"])

add("DSA", "medium", "What is the difference between a min-heap and a max-heap?",
    "In a min-heap, the root is the smallest element; in a max-heap, the root is the largest", ["They are the same data structure", "Min-heaps are faster", "Max-heaps use less memory"],
    "Both support O(log n) insert and O(1) peek at the root element.")

add("OS", "medium", "What is a pipe in Unix?",
    "A mechanism for inter-process communication where one process's stdout becomes another's stdin (e.g., ls | grep txt)", ["A network connection", "A file type", "A CPU instruction"],
    "Named pipes (FIFOs) allow communication between unrelated processes.", ["Google", "Apple"])

add("CN", "medium", "What is a VPN (Virtual Private Network)?",
    "A technology that creates an encrypted tunnel over the public internet to securely connect remote users or networks to a private network", ["A faster internet connection", "A type of DNS server", "A hardware network device"],
    "VPNs use protocols like IPsec, WireGuard, or OpenVPN for encrypted tunneling.", ["Cisco"])


# =============================================================================
#  Final validation and output
# =============================================================================

random.shuffle(questions)

# Ensure even distribution of answer indices
idx_counts = {0:0, 1:0, 2:0, 3:0}
for q in questions:
    idx_counts[q["answerIndex"]] += 1
print(f"Answer index distribution: {idx_counts}")

# Category summary
cats = {}
for q in questions:
    c = q["category"]
    d = q["difficulty"]
    cats.setdefault(c, {"easy":0, "medium":0, "hard":0})
    cats[c][d] += 1
for c, diffs in sorted(cats.items()):
    total = sum(diffs.values())
    print(f"  {c}: {total} ({diffs})")

print(f"\nTotal questions: {len(questions)}")

with open('/Users/whyush/Desktop/code-clash-v2/data/questions.json', 'w') as f:
    json.dump(questions, f, indent=2)

print("Written to questions.json successfully")
