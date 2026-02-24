# Requirements for Curating a Subset of 50 Repositories

## Objective

To select a subset of 50 repositories from the `codewiki_qa/qualified_repos.csv` file that is statistically representative of the repositories listed in `agent-prototypes/agent_prototypes/qabench/repos.csv`. The representativeness should be based on two key metrics: "lines of code" and "primary language".

## Methodology

The selection process will be based on ensuring that the distributions of the selected subset and the reference dataset are statistically similar. This will be achieved by comparing their Empirical Distribution Functions (EDFs).

### 1. Data Sources

*   **Reference Dataset:** `/usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/agent_prototypes/qabench/repos.csv`
*   **Candidate Dataset:** `/usr/local/google/home/guyu/Desktop/gcli/codewiki_qa/qualified_repos.csv`

### 2. Distribution Analysis

The following distributions will be analyzed and compared:

*   **Lines of Code:** The distribution of the `lines_of_code` column.
*   **Primary Language:** The distribution of the `primary_language` column.

### 3. Statistical Test for Similarity

The Kolmogorov-Smirnov (K-S) test will be used to compare the EDFs of the two samples for the "lines of code" metric. The K-S test is suitable for determining if two samples are drawn from the same distribution.

For the "primary language" metric, which is categorical, a Chi-Squared test will be used to compare the frequency distributions of the languages between the reference set and the selected subset.

### 4. Selection Criteria

A subset of 50 repositories will be selected from the candidate dataset such that:

1.  The p-value of the K-S test for the "lines of code" distribution between the selected subset and the reference dataset is greater than a significance level of 0.05. This indicates that we cannot reject the null hypothesis that the two samples are drawn from the same distribution.
2.  The p-value of the Chi-Squared test for the "primary language" distribution is also greater than 0.05.
3.  The selection process should aim to maximize the p-values for both tests to ensure the best possible match.

### 5. Process Outline

1.  Load both the reference and candidate datasets.
2.  For the "lines of code" metric, create the EDF for the reference dataset.
3.  For the "primary language" metric, calculate the frequency distribution for the reference dataset.
4.  Iteratively sample subsets of 50 repositories from the candidate dataset.
5.  For each sampled subset:
    a.  Calculate its "lines of code" EDF and "primary language" frequency distribution.
    b.  Perform the K-S test and Chi-Squared test against the reference dataset's distributions.
6.  The subset with the highest p-values (and both > 0.05) will be chosen as the final curated list. If multiple subsets satisfy this condition, one will be chosen at random.
