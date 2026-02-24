What I should not do:

spend more time to optimize for this data.
This data is far from complete, not perfect. If I were to spend more time to extract meaningful information, I'll ask to work on the real data set.

Here's what I need to submit

1. founder_score.csv: for each founder in inference set, give them a score and explanation
2. Readme.md:
   1. instruction on how to run the code (let the code be minimal)
   2. explain the approach and how this score was calculated, limitations of the method, data, and analysis identified. and how these can be addressed/improved.
   3. Include how the score was evaluated on the test set.
3. source code
4. follow_ups.md: answers the follow-up questions in ana_0.md
   - [ ] If you were to expand on your solution, in what ways might it be improved?
   - [ ] What other insights can you glean from the data that you have extracted?
   - [ ] How would you measure the performance of your solution?
   - [ ] What other data sources would you want to integrate to improve your scoring?
   - [ ] Imagine you now have 100 million founders to rank. How would you scale up your solution?
   - [ ] How would you productionize it and support real time scoring for new founders?
   - [ ] Let's say we are now looking to find candidates for other roles, such as C-suite, lead scientist, marketing, etc. How would you modify your solution to handle this? How would you modify your solution if you needed to rank founders within specific industries (Al, consumer, life sciences, etc)?


When I submit this today at 11 AM, here's what I would have done:

1. Score
   - [x] have a clearn pre-processed data set (before split)
     - expected 4766 rows
     - expected columns: person_id, company_id, performance, education_tier, education_level_score, industry, is_founder_of_target, label_company_id, label_max_founder_multiple, label_company_founded_year, label_company_industry, company_founded, label
     - stored_data:
       - xgboost/mlruns/models/founder_ranking_v4/prepared_founder_matrix_with_label.csv
   - [x] have a train/val/test split data set with augmented feature
     - expected 3812 rows in train, 477 rows in val, 477 rows in test
     - additional columns:
       - performance_features: founder_has_perf, founder_perf_mean, founder_perf_max, founder_perf_last
       - network_features: network_size_1st, network_quality_1st
       - team_features: team_size
     - stored_data:
       - xgboost/mlruns/models/founder_ranking_v4/test_post_split_features.csv
       - xgboost/mlruns/models/founder_ranking_v4/val_post_split_features.csv
       - xgboost/mlruns/models/founder_ranking_v4/train_post_split_features.csv
   - [x] have an evaluation criterion for the founder score I generate
    - [x] 1. NDCG@20
    - [x] 2. Recall@20
   - [x] Got a score with explanation from XGBoost
      - [x] Do a last iteration on XGBoost
      - [x] Distribution shift between training and inference.
        - Challenge:
          - Earlier companies have lots of exits while newer companies have fewer exits, this is expected behavior.
          - Founders may or may not have exited, and younger founders may have much less exits. Steve Jobs and Wozniak are two examples. They were both college dropouts and their first busines was blue box... It would take huge belief to invest in them - the Apple later on. So we need to be careful about the distribution shift.
          - Assuming multiples of 0.0 means company that have failed (i.e no return on capital).
          - How to handle?
            - reweighting training data: downweight successful founder in training; but this doesn't work well if success ratio in new founder is too low
            - importance weighting?
          - There comes the question - is the multiple actual multiples? i.e these recent companies have indeed failed (bankrupty with nothing to recoup) or don't have meaningful data yet?
      - [x] Know the answer to this
        - [x] XGBoost label is cast to int, which only has value from 0-7. I have 4000+ rows, how can I compute rank based on this label?
          - XGBoost predicts a score for each founder based on features, we can rank them by the score. It doesn't direclty predict the label.
      - [x] Remove founders that are in inference from the training set
      - [ ] Document thinkings and results of XGBoost Method
   - [x] Describe basic LLM based ideas for ranking founders
   - [x]  Got a score with explanation Yardstick
      - [x] Compute a simple heuristic based score, run this on the train/val/test set
      - [x] Compute recall, ndcg@10
   - [x] Design a general LLM based sliding window ranking on the founders got from XGBoost, evaluated the NDCG@10
      - [x] Know the answer to this
        - [x] The LLM based ranking is not deterministic, how can I make it deterministic?
2. Follow Ups
   - [ ] Answered all the follow-up questions in follow_ups.md
   - [ ] Distilled everything I have learned, read in the past week into the follow_ups.md
3. Readme
   1. [ ] instruction on how to run the code (let the code be minimal)
   2. [ ] explain the approach and how this score was calculated, limitations of the method, data, and analysis identified. and how these can be addressed/improved.
   3. [ ] Include how the score was evaluated on the test set (performance metrics, comparison with yardstick)
4. Source code
   1. [ ] Cleaned up source code to create a submission.zip
   2. [ ] Replicated this on google's laptop (i.e ran the source code independent of my local machine)
5. Submission
   1. [ ] Wrote an email to Marine, thanking them for the case study. indicate there were many follow-up questions and methods that I would like to try, give a few examples, and I would be happy to answer and discuss them.


### evaluation

NDCG measures how well the model’s ranking aligns with true relevance, focusing on the top-k positions.

- Relevance labels: Each founder’s label is an integer grade derived from `log1p(moic)` via `floor(log1p(moic))`, with non‑positive or missing values mapped to `0` (see `xgboost/src/models/metrics.py:9`). These grades are compatible with XGBoost’s ranking objective.
- Cutoff k: When the metric is specified as `ndcg@k` (e.g., `ndcg@20`), k is parsed from the string; if no `@k` is provided, k defaults to `10` (see `xgboost/src/models/metrics.py:31`).
- DCG@k: Sort items by predicted score descending, take the top k, then compute `DCG = sum((2^rel − 1) / log2(i + 2))` where `rel` is the relevance grade and `i` is zero‑based rank (see `xgboost/src/models/metrics.py:70-73`).
- IDCG@k: Compute DCG on the same items ordered by true relevance descending (the ideal ranking).
- NDCG@k: `NDCG = DCG / IDCG` with `0.0` returned if `IDCG` is `0` (see `xgboost/src/models/metrics.py:64-67`).

How it’s used in the notebook and training code:

- The ranker is trained with grouping and evaluated per group (e.g., per industry). For each group, NDCG@k is computed and then averaged to obtain a mean NDCG (see `xgboost/src/models/training.py:117-136`).
- The notebook passes the configured `eval_metric` (e.g., `ndcg@20`), and logs results; MLflow sanitizes names like `ndcg@20` to `ndcg_at_20` (see `xgboost/notebooks/GV_Exercise_Iteration4.ipynb:801`).
- analysis: calculate_mean_ndcg from models/metric.py

### yardstick

just use basic weighted heuristics to compute the score and rank founders, same ndcg@20 and recall@20 as XGBoost.