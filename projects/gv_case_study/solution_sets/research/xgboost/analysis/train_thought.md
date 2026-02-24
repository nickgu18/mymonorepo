<Instruction>
When reviewing the docs, for each question I have (tagged with '> question'), if there are no companion doc in /Users/yugu/Desktop/gehirn/gv_case_study/docs/xgboost/analysis/questions,
create one for me in the following format.

question_name.md

success criteria of answers: comprehensive, and also include a ELI5 section for beginners.

Question:

Analysis:

Conclusion:

And then put analysis and conclusions in the document. i.e

> question: ...
> [Answers](./questions/how_many_founders_have_this_issue.md)

</Instruction>

### My current problems

I didn't have too much experience with machine learning and model training. Right now, I have a full-fledged application using ML runs and packages as well as notebooks.

The challenge became for me to understand what each of these parameters means, what I am doing, and how is this pipeline working.

### my analysis questions

I have 4 training datasets, each with different columns:

1. company_info_training.csv
   - company_id
   - industry (IT, Healthcare, Other)
   - performance
2. target_variable_training.csv
   - company_id
   - industry (IT, Healthcare, Other)
   - company_founded
   - multiple
3. founder_experience_training.csv
   - person_id,order
   - company_id
   - title
   - job_type
   - start_date
   - end_date
   - is_c_suite
   - is_employee
   - is_executive
   - is_founder
   - is_on_board
4. education_training.csv, education.csv
   - person_id
   - education_tier
   - highest_level

### thoughts

#### thoughts 1

There is a challenge, founder_experience_training.csv has a person's full experience history, including when the person was founder and when they were not a founder. Further, I need to know how many of these founders have an actual job history with proper start and end dates (not null).

Some founders for example this one.

```
person_id,order,company_id,title,job_type,start_date,end_date,is_c_suite,is_employee,is_executive,is_founder,is_on_board
/p/SAZwFRMFCgQLMgkCADYaBA==,01,/c/SBVwHQ8dBA==,Board Member,board_member,2003-06-01,,False,False,False,False,True
/p/SAZwFRMFCgQLMgkCADYaBA==,02,/c/SBVwEwQFAAsKAxEVHzwrBQIEDwECFhMfPAc=,Board Member,board_member,2011-09-16,,False,False,False,False,True
/p/SAZwFRMFCgQLMgkCADYaBA==,03,/c/SBVwBAwdOhgHDBcKFzwRFB8GCQMeOg4YPA==,Board Member,founder,2013-01-01,,False,False,False,True,True
/p/SAZwFRMFCgQLMgkCADYaBA==,04,/c/SBVwFQUKFRwGGwAFHzAABAgN,Board Member,board_member,2013-07-09,,False,False,False,False,True
/p/SAZwFRMFCgQLMgkCADYaBA==,05,/c/SBVwGQQCFwkIGR0=,Board Member,board_member,2016-01-01,,False,False,False,False,True
/p/SAZwFRMFCgQLMgkCADYaBA==,06,/c/SBVwEwQFChwYBAs=,Scientific Advisor,advisor,2020-07-01,,False,,False,False,
/p/SAZwFRMFCgQLMgkCADYaBA==,07,/c/SBVwHQwGEAYGCQ==,Advisor,advisor,,,False,,False,False,
/p/SAZwFRMFCgQLMgkCADYaBA==,08,/c/SBVwGgAfDAcBDAk4HzEHFQIRHRsIFjgZOSsJDgQEGwU=,Chairman of the Board of Directors,board_member,,,False,,False,False,
/p/SAZwFRMFCgQLMgkCADYaBA==,09,/c/SBVwBAwdOhgHDBcKFzwRFB8GCQMeOg4YPA==,Board Member,board_member,,,False,,False,False,
/p/SAZwFRMFCgQLMgkCADYaBA==,10,/c/SBVwAAkOFwUACwwUHjoGPggKBQ==,Member of the Scientific Advisory Board,advisor,,,False,,False,False,
/p/SAZwFRMFCgQLMgkCADYaBA==,11,/c/SB9wFRMYAAYOAQ==,Senior Advisor,advisor,,,False,False,False,False,False
/p/SAZwFRMFCgQLMgkCADYaBA==,12,/c/SB9wHQ8fABoYCBYTKTcRAAcRAAwMFwIpLxUTHwsNHR4=,Advisor,advisor,,,False,False,False,False,False
/p/SAZwFRMFCgQLMgkCADYaBA==,13,/c/SB9wHAAfEQ0dDBY4ADoaFR4XDTAdBBUCMRETGA==,Scientific Advisory Board Member,board_member,,,False,False,False,False,True
/p/SAZwFRMFCgQLMgkCADYaBA==,14,,Member of the Advisory Board,advisor,,,False,,False,False,
/p/SAZwFRMFCgQLMgkCADYaBA==,15,,Professor Emeritus of Systems Biology,employee,,,False,,False,False,
```

has many experiences, some has start_date and end_date, some doesn't have end date, and some doesn't have start_date and end date.
Therefore, it's not possible to calculate the total career duration, and setting today as the end_date for these experiences introduces bias, because of two things:

1. end date could inflate experience duration
2. some doesn't event have start date so giving it an end date means nothing.

> question: how many founders have this issue?

Also, here a few things I need to know about this date:

1. what's the average experience per founder?
2. for each founder
   - what's the average number ofexperience with start but no end?
   - what's the average number ofexperience with end but no start?
   - what's the average number ofexperience with both start and end?
   - what's the average number ofexperience with no start and no end?

One thing I think of doing, is to use LLMs (gemini 2.5 flash preview) to scan each row, and fill in the is_xx columns based on the title and job_type.

which reminds me, there's already a column called is_founder...

[Answers](./questions/how_many_founders_have_this_issue.md)

#### thoughts 2

The challenge simply mentioned that I should create a function that takes in <founder_experience, founder_education, company_information> and returns a founder score with explanation.

I can use <founder_experience, founder_education, company_information> + <target_variable_training> to perform a training to optimize a model or some methods. That's it.

I think what they were expecting were simply a colab notebook that does this.
As well as a way to score incoming founders with the <founder_experience, founder_education, company_information> set.

so what I should is to collapse these <founder_experience, founder_education, company_information> 3 into a single table first.

```
Below is training data analysis:

Number of real_founders: 4772
Number of companies they founded: 4937
Number of founders with at least one company in target_variable_training: 4772
Number of real founders with at least one company in target_variable_training and company_info: 4772
Number of founders in training after removing inference founders: 4769
Number of founders in training after removing founders associated with inference companies: 4769

Below is inference data analysis:

Number of real_founders: 120
Number of companies they founded: 163
Number of founders with at least one company in target_variable_training: 3
Number of real founders with at least one company in target_variable_training and company_info: 3
['SAZwFRIDChwwCQQJHzoYGAoL' 'SAZwEBM0AQkZBAE4DD4GBgoXEQ4D'
 'SAZwBAQfFwccMg0CBDgaGAoL']
Number of companies in targets_variable that these founders are associated with: {'SBVwRVETOgECAAAVBTYCBA==', 'SBVwBAgFCgMGGQ=='}
```

Ok, previous analysis were not correct.

In the training data, founder_experience give me 4772 founders who have at least one foudner experience (is_founder = true).
Among these founders, all of them have education history, and they have started 4937 companies.
Now, all of them have at least one company in target_variable_training (which means there's multiple and company_founded year), and the same company exists in comapny_info.

This means for each founder in training, I can always get

<founder_id, education_features, job_experience_features, previous_company_features, network_features, last_started_company_id> - <company_founded_year, multiple>

And during inference time, i have

<founder_id, education_features, job_experience_features, previous_company_features, network_features, last_started_company_id> for running inference.

So in this sense, I can train a ranker model, R, that is evaluated using NDCG, and spews out a score for the feature set.

R(<founder_id, education_features, job_experience_features, previous_company_features, network_features, last_started_company_id>) = val_fid

Now, second question, how many of the inference data will be leaked into training?

3 founders have companies that are in the target_variable_training, these introduce leakage, and should be removed from training.

Now I have 4769 founders, with <founder_id, education_features, job_experience_features, previous_company_features, network_features, last_started_company_id>
pairs.

##### train and split

for the 4769 <founder_id, education_features, job_experience_features, previous_company_features, network_features, last_started_company_id>, I need to have a combined table.

Then I need to know foudner per industry split.

```
Number of valid training founders: 4769

Founder Counts per Industry:
industry
Information Technology    2941
Healthcare and Biotech    1019
Other                      811
Name: person_id, dtype: int64

Total assignments (sum of industry counts): 4771
Unique founders with at least one industry: 4769
Overlap (Founders in multiple industries): 2
```

> Question: what happens to these founders with overlapping industries when I train a per-industry ranker using XGBoost?
> [Answers](./questions/what_happens_with_overlapping_industries.md)

Ok, now it seems the best option is to do a per-industry split. Before that, I need to know the industry split for inference data.

```
For Inference Founders
inference_founders_real_filtered: (346, 12)
Index(['person_id', 'order', 'company_id', 'title', 'job_type', 'start_date',
       'end_date', 'is_c_suite', 'is_employee', 'is_executive', 'is_founder',
       'is_on_board'],
      dtype='object')
Last company per founder: (120, 12)
Index(['person_id', 'order', 'company_id', 'title', 'job_type', 'start_date',
       'end_date', 'is_c_suite', 'is_employee', 'is_executive', 'is_founder',
       'is_on_board', 'industry', 'performance'],
      dtype='object')
Valid founder companies with industry: (120, 14)
industry
Information Technology    75
Other                     32
Healthcare and Biotech    13
Name: person_id, dtype: int64
```

Since I have the per-industry split for inference data, I can split the training data into per-industry splits.

##### On performance

last part before I start training, I need to know how to handle `performance` column in training and inference data.

`* performance - A measure of the level of achievement for companies. Whereas multiple in target_variable_training.csv requires a company to have exited, this ‘performance’ measure applies to companies that have not exited as well. It is a related measure, but the exact details of the computation are not necessary to know. Just know a larger number indicates a better performing company. Many companies will have a Null for this field.`

According to the assignment, performance is an indicator for the level of achievenment of companies, including both exited and not exited as well.

> question: for inference data, how many founder have performance tied to their last founded company? how about across all the companies they have founded? For example, if a founder has 10 experiences, have founded 3 companies, and last one is a founder. I want to know if the 3 previous companies have performance provided in company_info.csv for this founder. and besides, I need to know this for both training and inference.
> [Answers](./questions/performance_coverage_for_founded_companies.md)

> question: building on last answer, how should I impute performance for founders who have no performance for any of their founded companies? since I have 88% of values available during training but only 40% of values available during inference.
> [Answers](./questions/how_to_impute_performance_for_missing_founders.md)

##### On multiples

target_variable_training.csv has a column called `multiple`. `* multiple - The return on capital venture capitalists achieved by investing in an early financing round of this company, expressed as a ratio of ($ returned / $ invested). A multiple of 1.0 for instance would indicate no profit, and no loss of money. This is the core metric that VCs want to optimize for.`

From previous analysis, I will have

R(<founder_id, education_features, job_experience_features, previous_company_features, network_features, last_started_company_id>) -> <company_founded_year, multiple>

Where train/test are split by industry.

This is the range of multiples `Raw Range: 0.0 - 2957.4959508655356`
This is the log1p range of multiples `Log1p Range: 0.0 - 7.9924362934714095`
This is the bin distribution of multiples

```
Bin Range: 0.0 - 8.0
multiple
(0.0, 0.5]    173
(0.5, 1.0]    175
(1.0, 1.5]    168
(1.5, 2.0]    137
(2.0, 2.5]    124
(2.5, 3.0]     66
(3.0, 3.5]     61
(3.5, 4.0]     34
(4.0, 4.5]     22
(4.5, 5.0]     18
(5.0, 5.5]     10
(5.5, 6.0]      3
(6.0, 6.5]      4
(6.5, 7.0]      2
(7.0, 7.5]      1
(7.5, 8.0]      1
Name: multiple, dtype: int64
/var/folders/37/4gxs5ryx1snb494502br5pn00000gn/T/ipykernel_63493/2327407702.py:31: FutureWarning: The default of observed=False is deprecated and will be changed to True in a future version of pandas. Pass observed=False to retain current behavior or observed=True to adopt the future default and silence this warning.
  binned_counts = log_multiple.groupby(pd.cut(log_multiple, bins)).count()
```

> question: how to handle multiple for the XGBoost (lambdaMART algorithm)?
> [Answers](./questions/how_to_handle_multiple_for_xgboost.md)

#### thoughts 3

Ok, prev two questions are answered. Now I need to start training.

Some key points to note:

- Training data has overlap with inference data, founders who have at least one founded comapny in training data (target_variable_training, company_info_training) should be removed.
- Split should be done per industry.
- Multiples are going to serve as the grade for XGBoost, and since the original value is highly skewed, I need to apply a log1p transform to it. np.log1p(x)=ln(1+x), so it will be 0 for 0 and 1 for 1, and then it will be a smooth curve for larger values
- there are many additional features that can be developed, but I'm going to start with the basic set of features.

There's the logical process of initial XGBoost training:

1. Load Data (training, inference and target_variable_training)
2. Clean Data
   2.1 Patch default values for founder_experience
3. Build Matrix
   3.1 Goal is to create a founder_matrix of {<person_id, features, company_id>, industry, company_founded, floor(log1p(multiple))} for training
   3.2 Creating <person_id, features, company_id>
   3.2.1 Start with founder_experience table, filter all founders with is_founder=true, get last company (determined by order) they founded
   3.2.2 combine education_training
   3.2.3 combine company_info (leave performance as is). additional features to add include `founder_has_perf`
   3.2.3.1 Optionally, compute aggregate performance features only when available, e.g.:
   3.2.3.2 `founder_perf_mean` = mean of `performance` over founded companies (NaN if none).
   3.2.3.3 `founder_perf_max` or `founder_perf_last` similarly defined.
   3.2.4 combine target_variable_training (same treatment for performance), remove companies that appeared in inference (founder's last company).
4. Train ranker
5. Test on inference data
