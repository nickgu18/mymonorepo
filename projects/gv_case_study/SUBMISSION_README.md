## Overall Walkthrough

**disclaimer**: So I had lots of fun exploring this problem, though sadly I only had few hours a day after my daughter sleeps to work on this. So there were several ideas I had that couldn't build out in time. What I describe in extras are things that were partially buildout earlier and I polished these up a bit. By no means these are part of submission, but I would like to hear thoughts on the ideas and how these problems are actually solved : D

### Where solutions are

- rankder_founder.csv in the google drive
- follow_ups folder
  - Contain follow up questions and answers
- other_ideas folder
  - Contain other ideas that I had but not entirely built out
  - Yardstick - a simple heuristic based solution
    - other_ideas/yardstick
  - LLM-based sliding window re-ranker - takes the result of Basic Ranker and slides up to re-rank
    - submission/other_ideas/llm_sliding_window_ranker
- source folder: directory to all the source code
  - Basic Ranker - a slightly tuned XGBoost Ranker to rank founders
    - source/xgboost/notebooks/GV_Exercise.ipynb
- submission.zip
  - everything packed into zip file

### Extras (Not part of solution)

- investor_view: a simple visualization site to show the results of ranked_founders

### Additional ideas to explore

*in addition to the follow up*

Perhaps we can evaluate and collect signals like 