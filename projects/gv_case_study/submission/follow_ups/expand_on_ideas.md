other_ideas directory list some ideas. There are many ways LLMs and Agents can be integrated to improve the solution. On a high level, it could be used to either 1. augment data 2. re-rank founders for model output 3. use as standalone ranking model. etc. On top of these, the current pipeline doesn't optimize model hyperparameters. This can be improved using autoML pipelines (i.e optuna).

Below I list some ideas that I think are interesting.

## LLM Re-ranking

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

A draft of this is implemented in other_ideas/llm_sliding_window_ranker

## Pairwise Ranking (Founder Arena)

not gonna implement.

the idea is simple: adopt a elo like rating system to rank founders.

Each founder has a certain set of properties, use LLM as a judge, provide it with

**jduge criteria**
1. critieria of good founder (from HBR for example)
2. current macro economic trends (interest rate for example)
3. Industry performance during different economic trends

**founder properties**
1. career experience
2. prevvious company performance
3. network analysis
4. education history
5. personality traits (analyze from social media, categorize using Merrill-Reid Social Personality Styles, i.e driver, analytical, expressive, amiable)
6. previous failures, i.e number of failed startups
7. expertise domain (not just from education, maybe infer this from their publications, blogs)
8. current startup domain if any

Then use LLM to do a battle between founders, answer given judge criteria, and founder properties of founder A and founder B.
Who are likely to build a company with better returns for investor with real exits?

Then the standard elo algorithm.

*note* LLm to augment data is discussed in [Data sources](follow_ups/data_sources.md)