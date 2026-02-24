## 1. First: pick the unit and the time you’re predicting *from*

Let’s fix the story:

> For each founder, we take a single **snapshot** of them just before the founding of one of their companies, and we want to predict how good that company’s outcome will be (or how good their *best* future outcome will be).

That means:

* Each founder appears **once** in the training data.
* Each row has:

  * an **label_company_founded_year** (you can use the founding year of the label company),
  * features built from information **up to that label_company_founded_year**,
  * a label that is the **outcome observed after** that date.

You have two choices for the label company per founder:

1. Last labeled company (what your code already does).
2. **Best exit (max multiple) company**.

If you pick **max multiple** as the label, the label_company_founded_year for that founder should be the **founding year of that best company**. That removes the conceptual “time” flaw: you’re not pretending to predict a 2015 exit using a 2000 snapshot; you’re using a 2015 snapshot to predict the eventual outcome of that 2015-founded company.

So per founder:

* Identify the company with the **highest multiple (max_founder_multiple)** among their founded companies.
* Set:
  * `label_max_founder_multiple = that company’s multiple`
  * `label_company_id = that company`
  * `label_company_founded_year = company_founded of the company with max_founder_multiple`
  * `label_company_industry = industry of the company with max_founder_multiple`

This is all done **before any train/val/test split**. You’re just defining what each training row *is*.

## 2. Before Split - Initial Founder Matrix

Once you’ve chosen the label company and its founding year per founder, you now have a clean target snapshot:

For each founder:

* `person_id`
* `label_max_founder_multiple`
* `label_company_id`
* `label_company_founded_year`
* `label_company_industry`

Now you build the **founder feature matrix as of label_company_founded_year**. That initial matrix should contain **only things that don’t require seeing the rest of the dataset**:

Examples:

* Education:
  * `education_tier`
  * `education_level_score`
* Experience counts/flags up to label_company_founded_year:
  * number of founder roles before/label_company_founded_year
  * number of companies founded before/label_company_founded_year
  * boolean “has any company with performance info” (using only roles ≤ label_company_founded_year)
* Simple company metadata of the label company:
  * `performance` of the label company (if you choose to use it)

You can calculate all of these **pre-split** because:

* They are computed per founder (and sometimes per company),
* They don’t require knowing the distribution of other founders,
* They don’t require training-set statistics.

So your “initial founder-level matrix” is:

> One row per founder, with:
>
> * person_id
> * all per-founder/per-company features that are local and time-respecting
> * the raw label (`label_max_founder_multiple`) attached as a column (but you won’t use it to *compute* features).
> * label_company_industry, label_company_founded_year, label_company_id

This is the dataset you will split.

## 3. Actual Split

Once you have that founder matrix, you:

1. **Sort** founders by `label_company_founded_year` within each `industry`.
2. **Temporal split**:

   * Oldest 70% of founders → train
   * Next 15% → validation
   * Newest 15% → test

At this point it is perfectly fine that the label (`label_max_founder_multiple`) is already sitting in the table:

* Splitting is just slicing rows.
* You’re not using test labels to influence train features or thresholds.
* Computing the label itself didn’t require seeing test features; it only used the founder’s own companies from the targets file, which is information legitimately used for supervision.

So you **do not** need to postpone label construction until after the split. What must be split-aware is any transformation that uses *global statistics* or *cross-founder structure* (scaling, network centrality, etc.), not the label.

## 4. Post Split - What to add *after* the split

Now you have three sets: train/val/test, each the same schema: features + label + label_company_founded_year.

On top of that you can safely layer any transformations that need to be “fit”:

- performance features
  - founder_has_perf
  - founder_perf_mean
  - founder_perf_max
  - founder_perf_last
- network features
  - network_quality_1st 1st degree network quality
  - network_size_1st 1st degree network size
- team features
  - team_size

These should be:

1. **Fit on train only**
   For example, compute means / std devs / graph scores / bucket edges *only* on the train founders.

2. **Applied to val/test** using those train-derived params.