# Installation Instruction

run `make install` in the source folder
select kernal .venv and run the notebooks

# My approach

## overall approach

**problem framing**: what is the problem, and how can we solve it?
This is a ranking problem where we score founders to prioritize outreach. We can use multiples on invested capital from the target variable training dataset as the performance indicator, as it reflects founders' ability to generate capital returns for VCs.

**initial analysis**: what issue about the data was found? how does this affect the problem framing?
(I did an analysis of the dataset, [notebook](xgboost/notebooks/data_analysis.ipynb)).

**how to evaluate performance**:
Before diving deep I need to understand how to evaluate the performance of the model. This is captured in [Measure performance](follow_ups/measure_performance.md). In addition, there needs to be a way to place the founders into respective order so that I can evaluate the performance.

Here I used max multiple that founder has acheived (derived from target_variable) as the performance indicator. Since this is also what VC's care about. This file also has founding year which helps with PIT calculation, to prevent lookahead bias.

**how to split data**:
ultimate goal is to score and rank founders so investors know who to reach out to. however, startups are from different industries which have very different factors (i.e regulation, recation to interest rate, growth rate, etc.). therefore, in my thinking the ranking should probably be industry specific.

**data cleaning and preparation**:
I focused on ensuring data integrity and preventing lookahead bias. Missing founding years were dropped (minimal impact, < 0.2% of data), and missing industries were labeled as "Other". The data was sorted by industry and founding year to allow for temporal splitting. Crucially, all feature computations (team size, network, performance) use a cut-off year based on the founder's current company's founding year to ensure no future information is used.

**feature engineering**:
I engineered several categories of features to capture different aspects of a founder's potential:
- **Team**: Size of the founding team at the time of founding.
- **Network**: Size and quality of the founder's professional network, derived from co-worker overlaps and their education tiers.
- **Performance**: Aggregated performance (mean, max, last) of the founder's previous companies.
- **Experience**: Total years of experience and counts of roles held (C-suite, executive, founder, etc.) prior to the current company.

**specific methods**:
I implemented an XGBoost Ranker to predict the relative ranking of founders within their industry cohorts. The model was trained to optimize NDCG, which is appropriate for ranking problems with graded relevance (multiples). I also used SHAP (SHapley Additive exPlanations) to interpret the model's predictions and identify the most influential features for each founder, adding these explanations to the final output.

### Method shortcomings

`It’s okay if your model has limitations as long as you understand its shortcomings and are able to
further discuss where and how it might be improved`

**limitation - distribution shift**

*problem*
Temporal distribution shift. The training founders are mostly from 1980–2015 and therefore have many exits and higher label_max_founder_multiple values. The validation founders are from about 2014‑2018 and the test founders are from 2017‑2024. 

Because venture outcomes take years to realise, most of the recent founders in the test split have no big exits yet. After doing per industry split by year, the hold out test comprised of founders with companies founded later in time and have less exits (or bankrupted more perhaps) - in any rate, there were predominant zero multiples (log1p) especially for Other industry and made it harder to to effectiv training and prediction.

Models trained on older data with many successful exits will over‑estimate the performance of recent founders and generalise poorly on the newer cohort.

*potential solution*
For scenario like this we can either reweight the training data to balance the class distribution, or use a stratified split to ensure that the validation and test sets have a similar distribution of classes as the training set.
Alternatively, we could get proxy labels (or get more data on multiples)

In addition, some industry-by-year cohorts (especially the most recent vintages) have almost all labels at the lowest grade. In those near-all-zero groups, NDCG and recall are not very informative (they collapse to 0.0 even if the model is doing as well as possible), and mean metrics across industries can be dragged down. Performance on these very recent cohorts is therefore structurally constrained by the lack of realised outcomes, which should be called out when reporting results.

**limitation - data handling**

*problem*
Missing founder years were dropped because there were only 3/2000. While safe, this might discard valuable data. In addition, the dataset has a significant class imbalance with many zero multiples, making it hard for the model to learn.

*potential solution*
Impute missing founding years using other signals (e.g., first education date + 22 years, or median founding year for the industry) and add a boolean flag for imputed data.

For the label imbalance, we can either reweight the training data to balance the class distribution, or use a stratified split to ensure that the validation and test sets have a similar distribution of classes as the training set. Alternatively, we could get proxy labels (or get more data on multiples)

**limitation - hyperparameter tuning**
*problem*
A model like XGBoost ranker can have many different paramters that needs to be tuned.

*potential solution*:
A full process would include autoML for paramter tuning (on validation set) since I have already train/val and hold out test set. optuna for example.

**limitation - noisy features**

*problem*
Many features are noisy or missing. Only ~60% of companies have performance data, and many founder roles lack clear start/end dates, making it hard to calculate precise tenure.

*potential solution*
1. Deep research to fill in missing dates and roles.
2. Integrate external data sources like Crunchbase for better company metrics (revenue, ARR, funding rounds).

**limitation - evaluation metric**

*problem*
I optimized for NDCG, which is good for general ranking. However, in VC, we are often looking for the "outliers" (unicorns). NDCG might treat a miss on a 100x return the same as a miss on a 10x return if they are both ranked low.

*potential solution*
Incorporate metrics like Precision@K or a custom loss function that heavily weights top-tier returns to better align with the venture capital business model.

### follow ups
Links to each follow-up:
   - If you were to expand on your solution, in what ways might it be improved?
      - [Expand on ideas](follow_ups/expand_on_ideas.md)
   - What other insights can you glean from the data that you have extracted?
      - [Data insights](follow_ups/data_insights.md)
   - How would you measure the performance of your solution?
      - [Measure performance](follow_ups/measure_performance.md)
   - What other data sources would you want to integrate to improve your scoring?
      - [Data sources](follow_ups/data_sources.md)
   - Imagine you now have 100 million founders to rank. How would you scale up your solution?
      - [Scale 100M founders](follow_ups/scale_100m.md)
   - How would you productionize it and support real time scoring for new founders?
      - [Productionize real time](follow_ups/productionize_realtime.md)
   - Let's say we are now looking to find candidates for other roles, such as C-suite, lead scientist, marketing, etc. How would you modify your solution to handle this? How would you modify your solution if you needed to rank founders within specific industries (Al, consumer, life sciences, etc)?
      - [Roles and industries](follow_ups/roles_industries.md)
