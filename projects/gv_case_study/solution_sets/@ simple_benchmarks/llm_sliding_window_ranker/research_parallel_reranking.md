# Parallel Reranking Algorithms for LLMs

## Overview
To speed up the reranking of a large list of items using LLMs, we can leverage parallel processing. While a simple sliding window is sequential, algorithms like Merge Sort can be adapted for parallel execution.

## Proposed Algorithm: Parallel Merge Reranker

This approach adapts the classic Merge Sort algorithm to use an LLM as the comparator/merger.

### Phase 1: Parallel Block Reranking (Base Case)
1.  Divide the list of $N$ items into $B$ blocks of size $K$ (e.g., $K=10$).
2.  Send each block to the LLM in parallel to be sorted.
3.  **Result**: $B$ sorted blocks.
4.  **Time**: $1 \times \text{LLM\_latency}$ (with perfect parallelism).

### Phase 2: Parallel Merge
1.  Pair up the sorted blocks.
2.  For each pair, use the LLM to merge them into a single sorted block.
    *   *Note*: Since LLMs prefer listwise input, we can merge two sorted lists of size $K$ by feeding them both to the LLM and asking for a combined sorted list of size $2K$ (if within context limits), or by using a streaming merge approach with smaller windows.
3.  Repeat until a single sorted list remains.
4.  **Time**: $\log_2(B) \times \text{LLM\_latency}$.

### Total Time Complexity
*   **Sequential Sliding Window**: $O(N)$ LLM calls, sequential.
*   **Parallel Merge**: $O(\log N)$ depth of LLM calls (with parallel execution).

## Comparison

| Algorithm | Parallelizable? | Total LLM Calls | Wall-clock Depth |
| :--- | :--- | :--- | :--- |
| **Sliding Window** | No | $N - K + 1$ | $O(N)$ |
| **Block Parallel** | Yes | $N/K$ | $O(1)$ (but not fully sorted) |
| **Parallel Merge** | Yes | $O(N)$ | $O(\log N)$ |

## Tournament Ranker (Alternative for Top-K)
If we only need the top-K items, a tournament-style bracket is even more efficient.
1.  Run parallel brackets of size $K$.
2.  Take the winners of each bracket and run a new bracket.
3.  Repeat until top-1 is found.
4.  To find top-K, we may need to run multiple rounds or maintain a heap.
