# How would you measure the performance of your solution?

The evaluation needs to answer: If we deployed this model on a new batch of founders, would it rank the highest-multiple founders near the top?

There were a few considerstions listed below:

1. a realistic hold-out

Random splitting would result in a set that mixes performance across different time periods.
Startups are affected by global trends, policy periods like zero interest rates, technology cycles (like gartner hype cycles). So I think it's better to not mix founders from different era/time periods.

Since company_founded year is provided in target_training_multiple, we can use that to split the data (only 3/2000 misses this value so these are dropped).
Sort founders by company_founded year, and then train on the earlier years (say, 70% oldest), validate on the middle (15%), and test on the most recent 15%.

2. ranking metrics

Evaluating a ranker requires more than just accuracy; we care about the order of the list.
NDCG is the standard for this, as it penalizes the model heavily for missing the best founders at the top.

Practically, we also care about 'hit rate' in our outreach.
So I tracked Top-k recall: if we contact the top N predicted founders, how many actual high-performers do we find? This directly proxies the investment team's success rate.

3. recall

While ranking gives a good signal of how well the model is able to place the 'best founders' near the top, recall captures how many 'relevant' founders are placed at top k. Since return multiples are highly skewed, we used a log transformation and hence can set different return thresholds to capture recall and evaluate the model's performance.