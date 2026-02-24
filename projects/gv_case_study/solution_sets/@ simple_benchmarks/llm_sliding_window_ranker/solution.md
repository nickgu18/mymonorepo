Simple llm ranker and founder arena are quite LLM heavy.
A sliding window ranker can be used to reduce the LLM calls.

Once we have the initial ranked list of founders, we can do a sliding window ranking. Going from the bottom up, say maybe 10 founders at a time, and ask LLM to re-rank them based on the @founder_properties.

**founder_properties**
1. career experience
2. prevvious company performance
3. network analysis
4. education history
5. personality traits (analyze from social media, categorize using Merrill-Reid Social Personality Styles, i.e driver, analytical, expressive, amiable)
6. previous failures, i.e number of failed startups
7. expertise domain (not just from education, maybe infer this from their publications, blogs)
8. current startup domain if any

For example, we have 120 founder scores, when we slide 1 founder at a time from the bottom up, and we have 110 windows to rank. Each window contains 10 founders, that will be re-ranked and each slide will leave out one founder (last one).

Evaluation can be similarly done with NDCG as well as recall.

## what to implement

suppose you are given a csv file of founders, with columns like solution_sets/@ datasets/processed_data/test_post_split_features.csv as well as a column of founder scores.

You need to implement a sliding window ranker, that ranks the founders based on the founder scores. The founder scores are provided in /Users/yugu/Desktop/gehirn/gv_case_study/solution_sets/@ datasets/prediction_data/*_predictions.csv.

Each founder has a series of experiences given in solution_sets/@ datasets/training/founder_experience_training.csv

The goal is to write a sliding window re-ranker that does this for for a given prediction file and a corresponding founder experience file.

Use gemini-2.5-pro for this task and a modifiable sliding window (default 10).
Create a single notebook for this reranker-llm.ipynb and calcualte the final recall and ndcg score.

**important** during testing, only run this on validation set. (i.e val_post_split_features.csv, val_predictions.csv and related experiences from founder_experience_training.csv)

**success criteria**
1. The reranker should be able to take a prediction file and a founder experience file as input. Then produce a re-ranked list of founders.
2. The reranker should calculate the ndcg (default to k=20) and recall (default to k=20) score.
3. The reranker is tested to work on val_post_split_features.csv, val_predictions.csv and related experiences from founder_experience_training.csv.
4. The reranker should use the key provided in .env

**prompt**

use jinja template for prompt (j2)

```j2
### founder_properties
{% for founder in founders %}
Founder {{ founder }}: {{ founder_properties }}
{% endfor %}

### criteria of good founders

Use evidence-based criteria from entrepreneurship research and venture capital practice when evaluating founders. In general, prefer founders who, based on the provided @founder_properties, show strong long-term potential to build and scale a high-impact, ethical company rather than just short-term fundraising ability.

- Career experience  
  Favor founders with deep, *relevant* operating and leadership experience (e.g. building products, owning P&L, managing teams) in the same or adjacent industry to their current startup domain. Prior roles that involved high uncertainty, rapid learning, and accountability (e.g. early-stage operator, GM, product lead) are especially positive. Give extra weight when their experience directly exposes them to the customer problems they now want to solve.

- Previous company performance  
  Rank higher founders who have helped create or scale successful companies: evidence of revenue growth, strong unit economics, durable product-market fit, meaningful exits, or significant value creation for customers and employees. Treat “quick hype then collapse” or purely vanity outcomes as weaker than steady, compounding performance.

- Network quality and access  
  Prefer founders whose networks give them advantaged access to capital, talent, customers, and partners in the relevant ecosystem. Strong signals include: central or well-connected positions in founder / investor / operator networks, repeated collaborations with high-quality people, and bridges across domains that unlock distribution or insight. Large but shallow or irrelevant networks should count less than smaller, high-trust, high-relevance networks.

- Education and human capital  
  Treat education as one component of human capital, not a gatekeeper. Rank higher founders whose education (formal degrees, bootcamps, or equivalent self-directed learning) clearly builds capabilities that matter for their current or likely domains: technical depth, domain knowledge, analytical thinking, and the ability to learn quickly. Elite credentials alone without evidence of applied execution should not outweigh strong, practice-driven experience.

- Personality traits and working style  
  From the inferred personality traits and Merrill-Reid style (driver, analytical, expressive, amiable), favor patterns associated with high entrepreneurial performance: high conscientiousness, openness to new ideas, resilience under stress, internal locus of control, and willingness to take calculated risks while learning from feedback.  
  Drivers and expressives are often strong at vision, selling, and momentum; analyticals at rigorous thinking and decision-making; amiables at culture, retention, and stakeholders. Rank highest when a founder’s style matches the demands of their domain and they show emotional stability, self-awareness, and the ability to work with complementary personalities. Clearly toxic, unethical, or extremely volatile behavior is a strong negative signal regardless of other strengths.

- Track record with failure  
  Do **not** automatically penalize founders for prior failed startups. Research suggests that experience, including failure, can improve judgment, negotiation power, and execution in later ventures when the founder learns from it. Favor founders who explicitly show reflection, pattern-breaking, and better outcomes over time. Mark down only when there is a repeated pattern of similar failures, denial of responsibility, or no visible learning.

- Domain expertise and thought leadership  
  Prefer founders whose expertise domain (from experience, education, publications, OSS contributions, patents, blogs, talks, etc.) tightly overlaps with the technical, regulatory, or customer realities of their current or likely startup domain. Deep, hands-on, niche expertise that creates “earned secrets” (non-obvious insights about how the market or technology really works) should be weighted strongly.

- Current startup domain and founder–market fit  
  Rank founders higher when their current startup domain is a natural extension of their past experience, network, and motivations. Strong founder–market fit looks like: lived experience of the customer pain, nuanced understanding of the competitive and regulatory landscape, and clear advantages in distribution, product insight, or execution in that specific market. Penalize cases where the startup domain appears trendy but poorly aligned with the founder’s background and resources.

When making trade-offs, prioritize: (1) relevant track record of execution and learning (including from failure), (2) strong founder–market fit between skills, network, and domain, and (3) evidence of resilient, ethical, and collaborative behavior. Ignore demographic attributes (e.g., gender, ethnicity, age) and superficial status signals; base the ranking only on the substance of the provided @founder_properties.

### task
For all the provided founders in @founder_properties, please re-rank them from best to worst based on the @founder_properties and @criteria of good founders.

### output
```