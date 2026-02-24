=== Per-Industry NDCG@20 Scores ===
Healthcare and Biotech:
  Train: 0.2067 | Test: 0.4175
Information Technology:
  Train: 0.2605 | Test: 0.6553
Other:
  Train: 0.3795 | Test: 0.4967

=== Mean NDCG@20 ===
Train ndcg@20: 0.2822
Test ndcg@20: 0.5232

My train score is way lower than test, indicating underfitting.

### 1\. Why is the Train NDCG@20 lower than the Test NDCG@20?

You observed:

  * Train NDCG@20: 0.2822
  * Test NDCG@20: 0.5232

It is unusual for a model to perform significantly better on the test set than on the training set. In your case, this is almost certainly due to a significant **difference in the difficulty and label distribution** between the training and test sets, caused by the temporal split (80% older data for training, 20% newer data for testing).

#### The Impact of Label Distribution Shift

By analyzing the label breakdown you provided (`<data>`), we can see a dramatic shift in the proportion of founders with the lowest relevance grade (Label 0):

| Industry | Train (% Label 0) | Test (% Label 0) |
| :--- | :--- | :--- |
| Healthcare and Biotech | 45.9% (374/814) | **84.8%** (173/204) |
| Information Technology | 57.5% (1349/2348) | **92.5%** (544/588) |
| Other | 68.5% (443/647) | **98.1%** (159/162) |

**The test set is overwhelmingly composed of Label 0 observations.**

#### Why this makes the Test Set "Easier"

NDCG measures how well the model ranks relevant items (Labels \> 0) above irrelevant items (Label 0).

  * **Training Set (Harder):** The training set has a richer distribution of positive labels (1 through 7). The model must learn subtle differences to rank a '4' above a '2', which is a complex task. The model struggles with this complexity, resulting in a lower score.
  * **Test Set (Easier):** When 90%+ of the items are Label 0, the ranking task becomes much simpler. The model only needs to identify the few positive examples and place them above the mass of zeros. It doesn't need to be good at distinguishing *between* the positive grades.

This distribution shift is typical in temporal splits for venture capital data. Older companies (training set) have had time to mature and realize outcomes, while newer companies (test set) often haven't exited yet, resulting in more '0' labels.

### 2\. Why are the overall scores low?

A training score of 0.2822 strongly suggests **underfitting**. The model is not complex enough or the features are not informative enough to capture the patterns in the training data.

1.  **Feature Signal:** You are using a limited set of 7 features. Predicting the highly skewed outcomes of VC investments requires richer signals related to experience, networks, and company traction, which might be missing.
2.  **Task Difficulty:** Predicting extreme outlier successes (the highest relevance grades) is inherently difficult, as many factors (luck, timing, specific innovation) are not captured in the data.

### 3\. How to implement a Train, Validation, Test split?

With 4763 observations, a single train/test split is highly sensitive to distribution shifts, as you've observed. You need a robust strategy for hyperparameter tuning and evaluation.

#### Recommended Strategy: Temporal Train-Validation-Test Split

While K-Fold Cross-Validation is often recommended for smaller datasets, a temporal split is crucial in this scenario to simulate real-world performance (predicting future outcomes based on past data). We can introduce a validation set while maintaining the temporal order and industry stratification.

A recommended split is 70% Train, 15% Validation, and 15% Test.

**Implementation Steps:**

1.  **Sort by Time:** Sort the data by `company_founded`.
2.  **Stratify by Industry:** Perform the split within each industry group.
3.  **Split Temporally:** Assign the oldest data to training, the middle portion to validation, and the newest data to testing.

Here is a Python implementation demonstrating this logic:

```python
import pandas as pd
import numpy as np

def train_val_test_temporal_split(df, group_col='industry', time_col='company_founded', train_ratio=0.7, val_ratio=0.15):
    """
    Splits the dataframe into train, validation, and test sets per group, 
    respecting the temporal order.
    
    Args:
        df (pd.DataFrame): The input dataframe (must have 'company_founded' and 'industry').
        group_col (str): The column to stratify by.
        time_col (str): The column to sort by time.
        train_ratio (float): Proportion of data for the training set.
        val_ratio (float): Proportion of data for the validation set.
    
    Returns:
        tuple: (train_df, val_df, test_df)
    """
    # Handle missing time data and sort
    df_cleaned = df.dropna(subset=[time_col]).sort_values(by=time_col)
    
    train_dfs = []
    val_dfs = []
    test_dfs = []

    for group_name, group_df in df_cleaned.groupby(group_col):
        n_samples = len(group_df)
        n_train = int(n_samples * train_ratio)
        n_val = int(n_samples * val_ratio)
        
        # The remainder goes to test
        
        train_set = group_df.iloc[:n_train]
        val_set = group_df.iloc[n_train:n_train + n_val]
        test_set = group_df.iloc[n_train + n_val:]
        
        train_dfs.append(train_set)
        val_dfs.append(val_set)
        test_dfs.append(test_set)
        
    # Concatenate results and shuffle within each set (optional, but good practice)
    train_df = pd.concat(train_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    val_df = pd.concat(val_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    
    return train_df, val_df, test_df

# Example Usage (assuming 'training_df' is your DataFrame from the notebook):
# train_df, val_df, test_df = train_val_test_temporal_split(
#     training_df, 
#     group_col='industry',
#     time_col='company_founded',
#     train_ratio=0.7, 
#     val_ratio=0.15
# )
```

### Summary and Next Steps

  * **The discrepancy is due to the temporal split** creating an easier test set dominated by Label 0.
  * **The low scores indicate underfitting**, likely due to insufficient features.
  * **Implement the Train/Validation/Test split** shown above.
  * **Focus on Feature Engineering:** This is your highest leverage point. Explore richer features related to founder experience (duration, seniority, previous successes), network connections, and company details.
  * **Hyperparameter Tuning:** Use the new validation set to optimize your XGBoost parameters (e.g., using Optuna) to improve the model's ability to learn from the training data.