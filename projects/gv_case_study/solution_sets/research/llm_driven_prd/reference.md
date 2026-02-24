### **4.2 Architecture A: Pairwise Ranking Prompting (PRP)**

The most robust method for ranking with LLMs is **Pairwise Ranking Prompting (PRP)**. This technique decomposes the listwise problem into a series of binary comparisons.33

#### **4.2.1 The Mechanism: LLM as a Comparator Function**

In standard sorting algorithms (like QuickSort or MergeSort), the core operation is a comparison function cmp(a, b) that returns true if a \> b. In PRP, we replace this mathematical function with an LLM inference call.

The Prompt Template:  
System: You are an expert Venture Capitalist with a specialization in Seed Stage B2B SaaS.  
User: I will present two founder profiles. Your task is to identify which founder represents a higher expected return on investment.  
: {insert\_markdown\_table\_B}

Reasoning: Briefly analyze the strengths and weaknesses of each regarding Market Size and Founder-Market Fit.  
Decision: Return ONLY the identifier of the winner (A or B).

33

#### **4.2.2 Algorithms for Aggregation**

Since comparing every possible pair ($N^2$) is inefficient, we utilize efficient aggregation algorithms.

* **Tournament Sort:** Founders are paired randomly. The winners advance to the next round. This identifies the top candidate in $O(N)$ comparisons but is less effective at ranking the middle tier.35  
* **Bubble Sort / Insertion Sort:** Simple to implement but inefficient ($O(N^2)$).  
* **Merge Sort:** The optimal approach for full ranking. The list is recursively divided, and the LLM is used to merge sorted sub-lists. This achieves a full ranking in $O(N \\log N)$ complexity.38  
* **Elo Rating System:** Alternatively, one can treat the comparisons as matches in a game. Each founder starts with an Elo rating of 1000\. The LLM "judges" matches, and the ratings are updated. After sufficient simulations, the Elo scores provide a continuous ranking variable.40

### **4.3 Architecture B: Sliding Window Listwise Reranking**

For scenarios where pairwise comparison is too slow, the **Sliding Window** approach offers a compromise between speed and accuracy. This method leverages the LLM's ability to handle small lists (e.g., 5-10 items) effectively.13

#### **4.3.1 The Algorithm**

1. **Initial Retrieval:** Start with a list of $N$ candidates (potentially ranked by a cheaper model like XGBoost).  
2. **Windowing:** Select a window of size $w$ (e.g., 10\) starting at the bottom of the list.  
3. **Local Ranking:** Ask the LLM to rank these 10 candidates.  
4. **Sliding:** Move the window up by a step size $s$ (e.g., 5). The "winners" of the previous window are now compared against the next batch of candidates.  
5. **Iteration:** Repeat until the top of the list is reached. This ensures that the best candidates "bubble up" to the top through repeated comparisons.32

**Nuance:** The step size is critical. A small step size ensures more overlap and more robust comparisons but increases token costs. A large step size is faster but risks "stranding" a good candidate in a local maxima if they are never compared against the true top tier.13

### **4.4 Data Serialization: Markdown vs. JSON**

A subtle but high-impact optimization in LLM ranking is the format of the input data. While developers often default to JSON for structured data, research suggests that **Markdown Tables** are superior for LLM prompting.44

* **Token Efficiency:** JSON requires repetitive syntax (braces, keys for every field). Markdown tables use minimal characters (| and \-), reducing token usage by 15-30%. This allows more founders to fit into the context window or reduces the cost per inference.46  
* **Reasoning Performance:** LLMs (especially those trained on code and documentation) have a strong bias towards understanding tabular data presented visually in Markdown. Experiments show higher accuracy in extraction and reasoning tasks when data is presented in Markdown-KV (Key-Value) or Table format compared to raw JSON.44

### **4.5 Handling Subjectivity and Hallucinations**

To mitigate the stochastic nature of LLMs, two advanced techniques are recommended:

1. **Permutation Consistency Check:** When comparing A vs. B, run the prompt twice: once as "Compare A vs B" and once as "Compare B vs A." If the LLM chooses A in the first and B in the second (position bias), the result is discarded or treated as a "tie".33  
2. **Chain of Thought (CoT) Enforcement:** Forcing the model to output a "Reasoning" field *before* the "Decision" field significantly improves the logical consistency of the ranking. It forces the model to generate the latent variables (the "why") before committing to the classification.47