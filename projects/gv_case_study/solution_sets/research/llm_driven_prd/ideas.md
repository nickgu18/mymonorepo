LLM driven analysis is inherently non deterministic, but powerful.

Given the data set we have, here's how I'm thinking this LLM can work:

1. Features
- Use LLM to extract qualitatibe features from the dataset, such as position senority
- Calculate set of static features such as
    - founder network quality
        - Defined by average education_tier of first degree connections (worked at the same company, started at the same company)
    - founder experience
        - defined by average duration held for positions

2. Actual tuning with automl or dspy

Same year/industry split train and test.

Do pairwise comparision of founders, i.e cmp(F1, F2), which should give us a ranking of founders.

Test this ranking against ground truth (back test, determined by founder ranked by their company exists/multiples or performance)

3. Rank real data, with explanantion

4. follow up: founder arena