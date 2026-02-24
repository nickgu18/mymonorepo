The pipeline was Dropping 1198 rows with missing company_founded (25.12%).

However, in my initial analysis, I got

```
Below is training data analysis:

Number of real_founders: 4772
Number of companies they founded: 4937
Number of founders with at least one company in target_variable_training: 4772
Number of real founders with at least one company in target_variable_training and company_info: 4772
Number of founders in training after removing inference founders: 4769
Number of founders in training after removing founders associated with inference companies: 4769
```

This means my baseline approach of choosing only the last founded company for each founder is not a good idea.

The challenge I have is label construction.

**what I have**
- founder experience
- company info
- target_variable_training (exited multiples)

**what I need**
- A label for each founder that indicates the multiple they exited for the final company they founded.

**what I will do**

docs/xgboost/execution/issue_2025-11-23_21-46-14.md outline how the company in final founder_matrix is choosen (i.e using last founded company determined by order).

Since:
Each founder can have multiple experiences, where they are a founder (is_founder=True).
Only a subset of companies have multiples (exited).
Each founder have at least one company in their experience that appears in the target_variable_training.

Therefore:
A good label for founder rank, is the combined multiples of the companies that they founded that appears in the target_variable_training.
company_id is not a feature, but for simplcity, let's start this way:
For each founder, get the last company (ranked by `order` column) in their experience that appears in the target_variable_training.
This company's id, industry, company_founded, and multiple (exited) are used in the founder matrix.

After _prepare_split_frame from xgboost/src/data/splitters.py, I expect 4772 rows.