
# **Algorithmic Alpha: A Comprehensive Framework for Quantitative Founder Ranking in Venture Capital**

## **1\. Introduction: The Quantitative Turn in Venture Capital**

The venture capital (VC) industry has historically operated on a paradigm of artisan selection—a process dominated by intuition, pattern recognition, and the cultivation of deep personal networks. For decades, the evaluation of a startup founder was considered an irreducible human task, one relying on "gut feel" and qualitative assessment of character, vision, and grit. However, the exponential growth in startup formation, coupled with the digitization of early-stage data, has precipitated a structural shift toward quantitative methodologies. The modern investment landscape is increasingly defined by "Algorithmic VC," where the objective is not merely to identify good companies but to systematically rank investment opportunities to maximize portfolio alpha.1

This report addresses the technical challenge of automating founder selection through the lens of Information Retrieval (IR). Specifically, it reframes the venture capital investment process as a **Learning to Rank (LTR)** problem. Unlike traditional classification (predicting binary success/failure) or regression (predicting exact valuation), ranking algorithms optimize for the relative ordering of candidates, ensuring that the most promising opportunities appear at the top of the deal flow funnel.3

We explore two distinct but complementary computational pathways for solving this founder ranking problem. The first utilizes **Traditional Machine Learning**, specifically Gradient Boosted Decision Trees (GBDT) and the LambdaMART algorithm, to process structured, quantitative signals. The second leverages **Large Language Models (LLMs)** to perform reasoning over unstructured narrative data, utilizing advanced prompting strategies like Pairwise Ranking Prompting (PRP) and listwise reranking. By synthesizing these approaches, we derive a robust, hybrid architecture capable of discerning signal from noise in the high-dimensional, sparse-data environment of early-stage investing.5

### **1.1 The Business Case for Ranking vs. Scoring**

A common misconception in early attempts at quantitative VC is the reliance on "scoring" models—assigning an absolute probability of success to a single startup in isolation. While intuitively appealing, pointwise scoring fails to capture the competitive, power-law dynamics of venture capital. A VC fund does not invest in a vacuum; it invests in a cohort. The critical decision is not "Is Company A good?" but rather "Is Company A better than Company B, given our limited capital and time?".4

Ranking algorithms address this by minimizing the number of "inversions"—instances where a lower-quality startup is ranked higher than a higher-quality one—rather than minimizing the error of a predicted valuation. This aligns the mathematical objective function with the economic reality of the fund manager, whose primary constraint is attention, not capital. By deploying these systems, firms like Correlation Ventures and Google Ventures have demonstrated that data-driven approaches can significantly accelerate the screening process, reducing decision times from weeks to hours while maintaining or exceeding the performance of human selectors.1

---

## **2\. Theoretical Framework: Learning to Rank (LTR) in Finance**

To implement a founder ranking system, one must first ground the application in the theoretical principles of Learning to Rank (LTR). LTR is a subset of supervised machine learning used extensively in search engines and recommender systems. In the context of a search engine, the system ranks web pages based on relevance to a user's query. In the context of venture capital, the system ranks founders based on relevance to the fund's investment thesis.8

### **2.1 The Taxonomy of Ranking Approaches**

The literature classifies LTR algorithms into three primary categories based on their training objective and loss function: Pointwise, Pairwise, and Listwise. Understanding the distinction between these is critical for selecting the appropriate architecture for founder evaluation.9

#### **2.1.1 Pointwise Approach**

The pointwise approach treats the ranking problem as a standard regression or classification task. Each founder-startup pair is considered independently.

* **Mechanism:** The model predicts a score $s(x)$ for a founder $x$. The loss function (e.g., Mean Squared Error) minimizes the difference between the predicted score and the ground truth label $y$.  
* **Limitations in VC:** This approach ignores the relative order between candidates. For example, if the model predicts a success probability of 0.8 for a "Unicorn" and 0.7 for a "Decacorn," the error might be small in absolute terms, but the ranking is catastrophic if it leads to passing on the Decacorn. Pointwise models often expend computational resources refining the calibration of scores that are irrelevant to the final sorting.8

#### **2.1.2 Pairwise Approach**

The pairwise approach approximates the ranking problem by reducing it to a binary classification of pairs.

* **Mechanism:** The model accepts two founders, $x\_i$ and $x\_j$, and predicts the probability that $x\_i$ is a better investment than $x\_j$. The objective is to minimize the number of misclassified pairs (inversions).  
* **Relevance to Founders:** This mimics the human investment committee process, which often involves comparing deal flow: "Is the team from Stanford working on Generative AI stronger than the team from MIT working on Quantum Computing?" The pairwise approach focuses the model's learning capacity on the *boundary* between candidates rather than their absolute value.4 This is the foundation of the LambdaMART algorithm utilized in XGBoost.8

#### **2.1.3 Listwise Approach**

The listwise approach treats the entire list of candidates as the input sample and optimizes a ranking metric directly.

* **Mechanism:** The loss function is defined on the permutation of the list, attempting to maximize metrics like NDCG (Normalized Discounted Cumulative Gain) directly.  
* **Challenges:** While theoretically optimal, listwise approaches are computationally expensive and difficult to optimize due to the non-differentiable nature of sorting operations. However, recent advances in LLMs have reinvigorated listwise ranking via sliding window techniques, allowing models to reason about global context within a local window.9

### **2.2 Evaluation Metrics: Beyond Accuracy**

In ranking problems, standard accuracy (e.g., "Did we predict the outcome correctly?") is insufficient. We require metrics that weigh the position of successful candidates.

#### **2.2.1 Normalized Discounted Cumulative Gain (NDCG)**

NDCG is the gold standard for evaluating ranking quality. It operates on the premise that highly relevant items must appear at the top of the list, and their value diminishes logarithmically as they fall down the ranks.14

$$\\text{DCG}\_p \= \\sum\_{i=1}^{p} \\frac{rel\_i}{\\log\_2(i+1)}$$  
Where $rel\_i$ is the graded relevance of the result at position $i$. In VC, $rel\_i$ might be the Multiple on Invested Capital (MOIC). If a startup returning 100x capital appears at rank 50, the $\\log\_2(51)$ denominator heavily penalizes the algorithm's score. If it appears at rank 1, the penalty is minimal. This aligns perfectly with the "Power Law" of venture returns, where missing a top-tier deal is the costliest error.15

#### **2.2.2 Mean Average Precision (MAP)**

MAP focuses on binary relevance (Success/Failure). It measures the precision at every position where a relevant document is retrieved and averages these scores. While useful, NDCG is generally preferred in VC contexts because it supports graded relevance (distinguishing between a 3x exit and a 100x exit), whereas MAP typically treats all successes equally.14

---

## **3\. Pathway 1: Traditional Machine Learning with XGBoost**

For quantitative founder ranking utilizing structured data, **Gradient Boosted Decision Trees (GBDT)**—specifically the implementation within **XGBoost**—represents the industry standard. This section details the implementation of the **LambdaMART** algorithm, a pairwise ranking method that combines the gradient boosting framework with a ranking-specific cost function.

### **3.1 The LambdaMART Algorithm**

LambdaMART is an adaptation of MART (Multiple Additive Regression Trees) where the gradient used to train the trees is derived from the "Lambda" rank.

* **The Physics of Ranking:** Conceptually, one can imagine the candidates as particles on a line. The "Lambda" ($\\lambda$) is a force vector applied to each candidate. If a candidate is ranked lower than it should be, a positive force pushes it up; if it is ranked higher than it should be, a negative force pushes it down.  
* **Pairwise Gradient:** The magnitude of this force is determined by the change in the ranking metric (e.g., $\\Delta NDCG$) that would result from swapping a pair of items. If swapping Founder A (currently rank 10\) with Founder B (currently rank 1\) results in a massive gain in NDCG, the gradient is large, forcing the model to correct this error aggressively in the next tree iteration.8

### **3.2 Data Construction and the "Group" Concept**

A critical implementation detail often overlooked in basic tutorials is the structure of the input data for learning-to-rank tasks. Unlike standard classification where data is independent and identically distributed (IID), ranking data is inherently grouped.17

#### **3.2.1 The Query ID (Group) Constraint**

In search engines, documents are grouped by "Query." In Venture Capital, founders must be grouped by **Cohort** or **Investment Window**. It is nonsensical to rank a Series A startup from 2015 against a Seed startup from 2023 directly, as market conditions and available data differ.

* **Implementation:** The dataset must be sorted by the Group ID. An auxiliary data structure (the group file) describes the boundaries of these groups.  
  * *Example:* If group \= , the algorithm treats the first 10 rows as one ranking contest, the next 25 as a second, independent contest, and so on.4  
* **Python Implementation:** In xgboost, this is passed via the group parameter in fit(). Failing to group data correctly introduces "look-ahead bias" and effectively breaks the pairwise comparison logic.4

### **3.3 Feature Engineering for Venture Scale**

The efficacy of the LambdaMART model is contingent on the quality of the features engineered from the raw data. Research indicates specific clusters of variables that possess high predictive power for startup success.1

#### **3.3.1 Founder Human Capital & Pedigree**

Quantitative analysis of founder backgrounds reveals that specific "pedigree" markers are highly correlated with fundraising success and eventual exit.

* **Level Segmentation:** Advanced models categorize founders into tiers.  
  * *L10 (Super Founders):* Previous exit \>$100M or IPO.  
  * *L9 (Unicorn Builders):* C-suite experience at \>$1B valuation companies.  
  * L8 (Disruptors): Founders with patents or significant technical innovations.  
    This hierarchical segmentation (L10-L1) allows the model to treat "experience" not just as years, but as a weighted quality metric.21  
* **Big Tech Effect:** Empirical studies show a statistical significance in the "Big Tech" background (e.g., prior employment at Google, Meta, Amazon). This variable serves as a proxy for technical rigorousness and network quality.23  
* **Team Dynamics:** Variables such as "Number of Co-founders" (solopreneurs typically underperform in VC models), "Years of Co-working," and "Skill Complementarity" (Technical \+ Business co-founder pairs) are critical.7

#### **3.3.2 Traction, Momentum, and "Soft Signals"**

Modern datasets allow for the quantification of momentum beyond financial metrics.

* **Digital Footprint:** The velocity of social proof is a leading indicator. Features should include the *first derivative* (rate of change) of LinkedIn followers, Twitter engagement, or Discord community size, rather than just static counts. For technical startups, GitHub star velocity is a proven proxy for product-market fit.20  
* **Network Centrality:** Features derived from graph analysis of the investor network. A founder backed by a "Tier 1" angel investor (high centrality) receives a higher weight. This requires constructing a co-investment graph and calculating centrality scores (Eigenvector or PageRank) for the founder's early backers.19

#### **3.3.3 Macro-Financial Context**

To normalize rankings across different economic cycles, features must embed market context.

* **Sector Heat:** Embedding the industry classification (e.g., "Generative AI") relative to the total venture funding volume in that quarter. This helps the model adjust for "hype cycles" where average valuations are inflated.22  
* **Geographic Arbitrage:** Distance to major capital hubs (San Francisco, New York, London) significantly impacts the probability of follow-on funding. While remote work is changing this, historical data still heavily favors proximity to capital.24

### **3.4 Implementation Strategy: XGBoost Configuration**

For a practitioner using Google Colab Pro, the implementation of this pathway involves specific configurations to enable GPU acceleration and optimized ranking objectives.

| Parameter | Value | Rationale |
| :---- | :---- | :---- |
| objective | rank:ndcg | Optimizes for the position of top-tier results, aligning with the power-law distribution of returns.11 |
| tree\_method | gpu\_hist | Utilizes GPU acceleration for histogram-based split finding, essential for large datasets on Colab Pro.8 |
| eval\_metric | ndcg@10 | Focuses validation on the top 10 candidates, ignoring the ordering of the "long tail" of rejection.11 |
| lambdarank\_unbiased | True | Enables unbiased LambdaMART to correct for position bias in the training data (e.g., if top-listed startups historically got more attention regardless of quality).12 |

**Implementation Note:** The rank:pairwise objective is also available and minimizes the number of pairwise inversions. However, rank:ndcg is generally preferred when graded relevance labels (e.g., 0=Fail, 1=Survival, 2=Exit, 3=Unicorn) are available, as it accounts for the magnitude of the success.28

---

## **4\. Pathway 2: Large Language Models (LLMs) for Ranking**

While traditional ML excels at processing structured signals, venture capital is intrinsically narrative-driven. The quality of a founder's vision, the clarity of their strategy, and the nuance of their market insight are encoded in unstructured text—pitch decks, interview transcripts, and essays. Large Language Models (LLMs) offer a mechanism to rank founders based on this semantic "Dark Data."

Using **Ollama** allows for the local deployment of powerful open-weights models (like Llama 3, Mistral, or Qwen) directly on Colab hardware. This circumvents the cost and privacy constraints of commercial APIs, enabling computationally intensive ranking architectures that require thousands of inference calls.30

### **4.1 The Limitation of Generative Ranking**

A naive approach to LLM ranking involves feeding a list of 50 founder profiles into the context window and prompting: "Rank these founders from best to worst." This typically fails due to three constraints:

1. **Context Window Saturation:** Even with large context windows, LLMs suffer from the "Lost in the Middle" phenomenon, where information in the center of the prompt is ignored or hallucinated.13  
2. **Stochasticity and Consistency:** LLMs are probabilistic. A single generation pass may produce a ranking that is inconsistent or structurally malformed (e.g., skipping rank \#4).33  
3. **Complexity of Comparison:** Ranking $N$ items requires $O(N \\log N)$ comparisons in a sorting algorithm. Asking the LLM to do this in one "shot" overloads its reasoning capabilities.35

To overcome these, we employ structured algorithmic frameworks that utilize the LLM strictly as a reasoning unit within a classic computer science sorting logic.

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

---

## **5\. Advanced Hybrid Architectures: The Retriever-Reranker Pipeline**

The optimal solution for a founder ranking problem at scale is neither pure ML nor pure LLM. It is a hybrid architecture that mirrors the structure of modern search engines (and indeed, the structure of a VC firm itself). We propose a **Retriever-Reranker** architecture.5

### **5.1 Stage 1: The Candidate Generator (XGBoost)**

* **Role:** The "Associate" Analyst.  
* **Input:** The entire universe of available startups (e.g., 10,000+ rows from Crunchbase/AngelList).  
* **Model:** XGBoost LambdaMART (rank:ndcg).  
* **Features:** Hard, quantitative metrics: Funding amounts, years of experience, sector growth rates, web traffic, social traction.  
* **Output:** A filtered list of the Top 100 candidates.  
* **Logic:** This stage is optimized for **Recall**. We want to ensure we don't miss any obvious hits, but we tolerate some false positives. It is fast, cheap, and deterministic.49

### **5.2 Stage 2: The Reasoning Engine (LLM)**

* **Role:** The "General Partner."  
* **Input:** The Top 100 candidates from Stage 1\.  
* **Model:** Llama 3 / Mistral (via Ollama).  
* **Features:** Unstructured narrative data: Pitch deck summaries, founder bios, competitive analysis texts, customer reviews.  
* **Method:** Pairwise Ranking (Tournament Sort) or Sliding Window Reranking.  
* **Output:** A final, strictly ordered list of the Top 20 investment targets.  
* **Logic:** This stage is optimized for **Precision**. It applies expensive, high-latency reasoning to differentiate between "good on paper" and "truly exceptional".6

### **5.3 Implementation Workflow (Python/Colab)**

The following conceptual workflow demonstrates how to integrate these tools using Python.

**Step 1: The Retriever (XGBoost)**

Python

import xgboost as xgb  
\#... Load data, sort by group...  
ranker \= xgb.XGBRanker(objective='rank:ndcg', tree\_method='gpu\_hist')  
ranker.fit(X\_train, y\_train, group=groups)  
scores \= ranker.predict(X\_candidates)  
\# Select top 50 candidates based on XGBoost scores  
top\_candidates \= candidates\_df.iloc\[np.argsort(scores)\[-50:\]\]

**Step 2: The Reranker (Ollama)**

Python

import ollama  
from itertools import combinations

def get\_winner(founder\_a, founder\_b):  
    \# Construct Markdown tables for A and B  
    prompt \= construct\_pairwise\_prompt(founder\_a, founder\_b)  
    response \= ollama.chat(model='llama3', messages=\[{'role': 'user', 'content': prompt}\])  
    return parse\_response(response)

\# Simple Tournament Sort Logic  
current\_round \= top\_candidates  
while len(current\_round) \> 1:  
    next\_round \=  
    for i in range(0, len(current\_round), 2):  
        if i \+ 1 \>= len(current\_round):  
            next\_round.append(current\_round\[i\])  
            break  
        winner \= get\_winner(current\_round\[i\], current\_round\[i+1\])  
        next\_round.append(winner)  
    current\_round \= next\_round  
      
final\_winner \= current\_round

30

### **5.4 Probabilistic Aggregation: Bradley-Terry Models**

For a more scientifically rigorous aggregation of the pairwise data from Step 2, one should utilize the Bradley-Terry-Luce (BTL) model. Rather than just declaring a "winner," the BTL model estimates the latent "skill" (or quality) parameter $\\lambda\_i$ for each founder such that the probability of Founder $i$ beating Founder $j$ is:

$$P(i \> j) \= \\frac{\\lambda\_i}{\\lambda\_i \+ \\lambda\_j}$$

Libraries like choix in Python allow you to feed in a dataset of pairwise comparisons (e.g., "A beat B", "B beat C", "A beat C") and mathematically derive the maximum likelihood ranking. This handles cyclic disagreements (where A \> B \> C \> A) more robustly than simple sorting.53

---

## **6\. Strategic Implications and Second-Order Insights**

Implementing an algorithmic ranking system in venture capital generates ripple effects that extend beyond simple efficiency gains. It fundamentally alters the nature of the investment thesis.

### **6.1 The Convergence Problem**

A common phenomenon in hybrid systems is the **Signal Divergence** between the ML and LLM models.

* **Scenario:** XGBoost ranks a founder highly because they have 3 prior exits and 10 years of experience (safe bet). The LLM ranks them poorly because their pitch deck is generic and lacks a unique insight (low upside). Conversely, the LLM might champion a college dropout with zero experience but a visionary manifesto (high risk, high reward).  
* **Insight:** This divergence is the "Alpha." A system that only selects founders where *both* models agree will result in a portfolio of "Consensus" bets—safe, but unlikely to return 100x. The most lucrative investments often lie where the quantitative signal is weak (or nascent) but the qualitative signal is deafening. Advanced implementation involves creating a "Disagreement Alert" that flags these specific divergences for human partner review.6

### **6.2 Bias Amplification and Ethical AI**

Automated ranking systems risk encoding and amplifying historical biases.

* **Mechanism:** If the XGBoost model is trained on historical VC data (which heavily favors male, white, Ivy League founders), the model learns that "Female \= Lower Probability of Series A." This is a statistical fact of the past, but a strategic error for the future.  
* **Mitigation:** The "Unbiased LambdaMART" objective helps, but true mitigation requires feature blinding.  
  * *Strategy:* Strip names, gender pronouns, and university names from the LLM prompts. Replace them with generic tokens (e.g., "\[Founder\]", "\[University\]"). This forces the LLM to rank based on the merit of the idea and the traction, not the demographic pattern matching of the past. This "Blind Audition" approach has been shown to significantly alter ranking outcomes in hiring and is equally applicable to VC.12

### **6.3 Future Outlook: Autonomous Agents**

The current state of the art is "Human-in-the-Loop" ranking. The trajectory, however, points toward **Autonomous VC Agents**. By integrating "Tool Use" (Function Calling), an LLM-based ranker could not just read a pitch deck, but autonomously browse the startup's website, test their API, check the founder's GitHub commit history, and query a vector database of competitors—all before generating a final ranking. This moves the system from "Passive Analysis" to "Active Diligence," creating a continuous, real-time leaderboard of global startup activity.30

## **7\. Conclusion**

The transition from intuition-based selection to algorithmic ranking is not merely a technological upgrade; it is an epistemological shift in how venture capital defines value. By adopting a **Learning to Rank** framework, investors acknowledge that the goal is not to predict the future with certainty, but to order the chaos of the present with discipline.

This report has outlined a comprehensive methodology for achieving this. We have deconstructed the mathematical superiority of **LambdaMART** for processing hard signals, leveraging the rank:ndcg objective to align algorithmic penalties with the power-law realities of venture returns. We have detailed the application of **Large Language Models** not as generative chatbuts, but as rigorous **Pairwise Comparators**, capable of extracting qualitative alpha from narrative data. Finally, we have proposed a **Hybrid Architecture** that fuses these distinct signals, utilizing the efficiency of XGBoost to filter noise and the reasoning depth of LLMs to identify outliers.

For the practitioner equipped with modern tools like Colab Pro and Ollama, this is no longer theoretical. The code, the algorithms, and the models are accessible. The competitive advantage now lies in the nuanced engineering of features, the careful construction of prompts, and the courage to trust the ranking when it diverges from the consensus.

### **Cited Sources**

1

#### **Works cited**

1. Applications of AI and Machine Learning in Venture Capital \- MLQ.ai, accessed November 18, 2025, [https://blog.mlq.ai/ai-machine-learning-venture-capital/](https://blog.mlq.ai/ai-machine-learning-venture-capital/)  
2. Predicting VC Success With Crunchbase Data, accessed November 18, 2025, [https://news.crunchbase.com/venture/vc-success-prediction-crunchbase-data-mason-lender/](https://news.crunchbase.com/venture/vc-success-prediction-crunchbase-data-mason-lender/)  
3. Ranking Basics: Pointwise, Pairwise, Listwise | Towards Data Science, accessed November 18, 2025, [https://towardsdatascience.com/ranking-basics-pointwise-pairwise-listwise-cd5318f86e1b/](https://towardsdatascience.com/ranking-basics-pointwise-pairwise-listwise-cd5318f86e1b/)  
4. Learning to Rank using XGBoost. sci-kit learn and Pandas | by Simon Lind | Predictly on Tech | Medium, accessed November 18, 2025, [https://medium.com/predictly-on-tech/learning-to-rank-using-xgboost-83de0166229d](https://medium.com/predictly-on-tech/learning-to-rank-using-xgboost-83de0166229d)  
5. Exploring the Impact of Large Language Models on Recommender Systems: An Extensive Review \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2402.18590v3](https://arxiv.org/html/2402.18590v3)  
6. Rethinking Hybrid Retrieval: When Small Embeddings and LLM Re-ranking Beat Bigger Models \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2506.00049v1](https://arxiv.org/html/2506.00049v1)  
7. Machine Learning About Venture Capital Choices \- Texas A\&M University Mays Business School, accessed November 18, 2025, [https://mays.tamu.edu/wp-content/uploads/2025/03/288-Machine-learning-about-VC-choices.pdf](https://mays.tamu.edu/wp-content/uploads/2025/03/288-Machine-learning-about-VC-choices.pdf)  
8. Learning to Rank with XGBoost and GPU | NVIDIA Technical Blog, accessed November 18, 2025, [https://developer.nvidia.com/blog/learning-to-rank-with-xgboost-and-gpu/](https://developer.nvidia.com/blog/learning-to-rank-with-xgboost-and-gpu/)  
9. Precise Zero-Shot Pointwise Ranking with LLMs through Post-Aggregated Global Context Information \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2506.10859v1](https://arxiv.org/html/2506.10859v1)  
10. Pointwise, Pairwise and Listwise Learning to Rank | by Mayur Bhangale \- Medium, accessed November 18, 2025, [https://medium.com/@mayurbhangale/pointwise-pairwise-and-listwise-learning-to-rank-baf0ad76203e](https://medium.com/@mayurbhangale/pointwise-pairwise-and-listwise-learning-to-rank-baf0ad76203e)  
11. XGBoost \- Learning To Rank \- Tutorials Point, accessed November 18, 2025, [https://www.tutorialspoint.com/xgboost/xgboost-learning-to-rank.htm](https://www.tutorialspoint.com/xgboost/xgboost-learning-to-rank.htm)  
12. Learning to Rank — xgboost 2.0.3 documentation, accessed November 18, 2025, [https://xgboost.readthedocs.io/en/release\_2.0.0/tutorials/learning\_to\_rank.html](https://xgboost.readthedocs.io/en/release_2.0.0/tutorials/learning_to_rank.html)  
13. Sliding Windows Are Not the End: Exploring Full Ranking with Long-Context Large Language Models \- ACL Anthology, accessed November 18, 2025, [https://aclanthology.org/2025.acl-long.8.pdf](https://aclanthology.org/2025.acl-long.8.pdf)  
14. Demystifying NDCG | Towards Data Science, accessed November 18, 2025, [https://towardsdatascience.com/demystifying-ndcg-bee3be58cfe0/](https://towardsdatascience.com/demystifying-ndcg-bee3be58cfe0/)  
15. Measuring Search Relevance, Part 2: nDCG Deep Dive \- Reddit, accessed November 18, 2025, [https://www.reddit.com/r/RedditEng/comments/y6idrl/measuring\_search\_relevance\_part\_2\_ndcg\_deep\_dive/](https://www.reddit.com/r/RedditEng/comments/y6idrl/measuring_search_relevance_part_2_ndcg_deep_dive/)  
16. Every Ranking Metric : MRR, MAP, NDCG \- YouTube, accessed November 18, 2025, [https://www.youtube.com/watch?v=2XegvMul\_mE](https://www.youtube.com/watch?v=2XegvMul_mE)  
17. Learning to Rank — xgboost 3.1.1 documentation, accessed November 18, 2025, [https://xgboost.readthedocs.io/en/stable/tutorials/learning\_to\_rank.html](https://xgboost.readthedocs.io/en/stable/tutorials/learning_to_rank.html)  
18. Understanding Groups in scikit-learn for XGBoost Ranking \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/68563115/understanding-groups-in-scikit-learn-for-xgboost-ranking](https://stackoverflow.com/questions/68563115/understanding-groups-in-scikit-learn-for-xgboost-ranking)  
19. Predictive Analytics in Venture Capital: A Technical Deep Dive for Tech Leaders \- Meroxa, accessed November 18, 2025, [https://meroxa.com/blog/predictive-analytics-in-venture-capital-a-technical-deep-dive-for-tech-leaders/](https://meroxa.com/blog/predictive-analytics-in-venture-capital-a-technical-deep-dive-for-tech-leaders/)  
20. What Matters Most? A Quantitative Meta-Analysis of AI-Based Predictors for Startup Success, accessed November 18, 2025, [https://ideas.repec.org/p/arx/papers/2507.09675.html](https://ideas.repec.org/p/arx/papers/2507.09675.html)  
21. Founder assessment using LLM-powered segmentation, feature engineering and automated labeling techniques \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2407.04885v1](https://arxiv.org/html/2407.04885v1)  
22. Factors Influencing Startup Success: A Quantitative Analysis, accessed November 18, 2025, [https://jabans.ir/wp-content/uploads/2024/12/Factors\_Influencing\_Startup\_Success\_A\_Qu.pdf](https://jabans.ir/wp-content/uploads/2024/12/Factors_Influencing_Startup_Success_A_Qu.pdf)  
23. Analysis of Founder Background as a Predictor for Start-up Success in Achieving Successive Fundraising Rounds \- Deep Blue Repositories, accessed November 18, 2025, [https://deepblue.lib.umich.edu/handle/2027.42/172876](https://deepblue.lib.umich.edu/handle/2027.42/172876)  
24. Startup-Success-Prediction-using-Machine-Learning \- GitHub, accessed November 18, 2025, [https://github.com/sumitjhaleriya/Startup-Success-Prediction-using-Machine-Learning](https://github.com/sumitjhaleriya/Startup-Success-Prediction-using-Machine-Learning)  
25. What Matters Most? A Quantitative Meta-Analysis of AI-Based Predictors for Startup Success, accessed November 18, 2025, [https://www.researchgate.net/publication/393685381\_What\_Matters\_Most\_A\_Quantitative\_Meta-Analysis\_of\_AI-Based\_Predictors\_for\_Startup\_Success](https://www.researchgate.net/publication/393685381_What_Matters_Most_A_Quantitative_Meta-Analysis_of_AI-Based_Predictors_for_Startup_Success)  
26. Algorithmic Identification of Relevant Investors Using Machine Learning | The American Journal of Management and Economics Innovations, accessed November 18, 2025, [https://www.theamericanjournals.com/index.php/tajmei/article/view/6558](https://www.theamericanjournals.com/index.php/tajmei/article/view/6558)  
27. Startup Success Prediction \- Kaggle, accessed November 18, 2025, [https://www.kaggle.com/datasets/manishkc06/startup-success-prediction](https://www.kaggle.com/datasets/manishkc06/startup-success-prediction)  
28. Learning to Rank — xgboost 3.2.0-dev documentation, accessed November 18, 2025, [https://xgboost.readthedocs.io/en/latest/tutorials/learning\_to\_rank.html](https://xgboost.readthedocs.io/en/latest/tutorials/learning_to_rank.html)  
29. LightGBM \- Ranking \- Tutorials Point, accessed November 18, 2025, [https://www.tutorialspoint.com/lightgbm/lightgbm-ranking.htm](https://www.tutorialspoint.com/lightgbm/lightgbm-ranking.htm)  
30. Using Ollama with Python: Step-by-Step Guide \- Cohorte Projects, accessed November 18, 2025, [https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide](https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide)  
31. Ollama Python Library Examples: Guide & Code Samples \- BytePlus, accessed November 18, 2025, [https://www.byteplus.com/en/topic/553253](https://www.byteplus.com/en/topic/553253)  
32. Full Ranking with Long-Context LLMs \- Emergent Mind, accessed November 18, 2025, [https://www.emergentmind.com/papers/2412.14574](https://www.emergentmind.com/papers/2412.14574)  
33. Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2306.17563v2](https://arxiv.org/html/2306.17563v2)  
34. What's the BEST local LLM for JSON output, while also being smart? \- Reddit, accessed November 18, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1ex6ngu/whats\_the\_best\_local\_llm\_for\_json\_output\_while/](https://www.reddit.com/r/LocalLLaMA/comments/1ex6ngu/whats_the_best_local_llm_for_json_output_while/)  
35. Tournament Sort \- OI Wiki, accessed November 18, 2025, [https://en.oi-wiki.org/basic/tournament-sort/](https://en.oi-wiki.org/basic/tournament-sort/)  
36. Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting, accessed November 18, 2025, [https://aclanthology.org/2024.findings-naacl.97/](https://aclanthology.org/2024.findings-naacl.97/)  
37. ielab/llm-rankers: Document Ranking with Large Language Models. \- GitHub, accessed November 18, 2025, [https://github.com/ielab/llm-rankers](https://github.com/ielab/llm-rankers)  
38. Sorting Algorithms in Python, accessed November 18, 2025, [https://realpython.com/sorting-algorithms-python/](https://realpython.com/sorting-algorithms-python/)  
39. Complete Guide on Sorting Techniques in Python \[2025 Edition\] \- Analytics Vidhya, accessed November 18, 2025, [https://www.analyticsvidhya.com/blog/2024/01/sorting-techniques-in-python/](https://www.analyticsvidhya.com/blog/2024/01/sorting-techniques-in-python/)  
40. Chatbot Arena and the Elo rating system \- Part 1 \- Yi Zhu, accessed November 18, 2025, [https://bryanyzhu.github.io/posts/2024-06-20-elo-part1/](https://bryanyzhu.github.io/posts/2024-06-20-elo-part1/)  
41. A Statistical Framework for Ranking LLM-Based Chatbots \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2412.18407v1](https://arxiv.org/html/2412.18407v1)  
42. Guiding Retrieval using LLM-based Listwise Rankers \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2501.09186v1](https://arxiv.org/html/2501.09186v1)  
43. LLM-Driven Product Recommendations \- Emergent Mind, accessed November 18, 2025, [https://www.emergentmind.com/topics/llm-driven-product-recommendations](https://www.emergentmind.com/topics/llm-driven-product-recommendations)  
44. Which Table Format Do LLMs Understand Best? (Results for 11 Formats) \- Improving Agents, accessed November 18, 2025, [https://www.improvingagents.com/blog/best-input-data-format-for-llms/](https://www.improvingagents.com/blog/best-input-data-format-for-llms/)  
45. Why Markdown is the best format for LLMs | by Wetrocloud \- The AI Stack for Automations, accessed November 18, 2025, [https://medium.com/@wetrocloud/why-markdown-is-the-best-format-for-llms-aa0514a409a7](https://medium.com/@wetrocloud/why-markdown-is-the-best-format-for-llms-aa0514a409a7)  
46. Markdown is 15% more token efficient than JSON \- OpenAI Developer Community, accessed November 18, 2025, [https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742](https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742)  
47. Top 10 LLM Benchmarking Evals.| by Himanshu Bamoria \- Medium, accessed November 18, 2025, [https://medium.com/@himanshu\_72022/top-10-llm-benchmarking-evals-c52f5cb41334](https://medium.com/@himanshu_72022/top-10-llm-benchmarking-evals-c52f5cb41334)  
48. LLM Context Engineering: a practical guide | by Zheng "Bruce" Li | The Low End Disruptor, accessed November 18, 2025, [https://medium.com/the-low-end-disruptor/llm-context-engineering-a-practical-guide-248095d4bf71](https://medium.com/the-low-end-disruptor/llm-context-engineering-a-practical-guide-248095d4bf71)  
49. Enhancing RAG Pipelines with Re-Ranking | NVIDIA Technical Blog, accessed November 18, 2025, [https://developer.nvidia.com/blog/enhancing-rag-pipelines-with-re-ranking/](https://developer.nvidia.com/blog/enhancing-rag-pipelines-with-re-ranking/)  
50. Building Contextual RAG Systems with Hybrid Search & Reranking \- Analytics Vidhya, accessed November 18, 2025, [https://www.analyticsvidhya.com/blog/2024/12/contextual-rag-systems-with-hybrid-search-and-reranking/](https://www.analyticsvidhya.com/blog/2024/12/contextual-rag-systems-with-hybrid-search-and-reranking/)  
51. RaCT: Ranking-aware Chain-of-Thought Optimization for LLMs \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2412.14405v3](https://arxiv.org/html/2412.14405v3)  
52. Ollama Python library \- GitHub, accessed November 18, 2025, [https://github.com/ollama/ollama-python](https://github.com/ollama/ollama-python)  
53. Optimal full ranking from pairwise comparisons \- Anderson Ye Zhang, accessed November 18, 2025, [https://andersonyezhang.github.io/PDF/ranking\_full.pdf](https://andersonyezhang.github.io/PDF/ranking_full.pdf)  
54. Small script to compute Bradley–Terry pairwise ranking model and upload results to Google Sheets \- GitHub, accessed November 18, 2025, [https://github.com/bjlkeng/Bradley-Terry-Model](https://github.com/bjlkeng/Bradley-Terry-Model)  
55. choix \- PyPI, accessed November 18, 2025, [https://pypi.org/project/choix/](https://pypi.org/project/choix/)  
56. Read Ollama in Action: Building Safe, Private AI with LLMs, Function Calling and Agents | Leanpub, accessed November 18, 2025, [https://leanpub.com/ollama/read](https://leanpub.com/ollama/read)  
57. Data-driven Investors \- AMF, accessed November 18, 2025, [https://www.amf-france.org/sites/institutionnel/files/private/2025-05/bonelli\_m.\_2024-data-driven\_investors.pdf](https://www.amf-france.org/sites/institutionnel/files/private/2025-05/bonelli_m._2024-data-driven_investors.pdf)  
58. castorini/rank\_llm: RankLLM is a Python toolkit for reproducible information retrieval research using rerankers, with a focus on listwise reranking. \- GitHub, accessed November 18, 2025, [https://github.com/castorini/rank\_llm](https://github.com/castorini/rank_llm)  
59. LLM Output Formats: Why JSON Costs More Than TSV | by David Gilbertson \- Medium, accessed November 18, 2025, [https://david-gilbertson.medium.com/llm-output-formats-why-json-costs-more-than-tsv-ebaf590bd541](https://david-gilbertson.medium.com/llm-output-formats-why-json-costs-more-than-tsv-ebaf590bd541)  
60. LLM Comparator is an interactive data visualization tool for evaluating and analyzing LLM responses side-by-side, developed by the PAIR team. \- GitHub, accessed November 18, 2025, [https://github.com/PAIR-code/llm-comparator](https://github.com/PAIR-code/llm-comparator)