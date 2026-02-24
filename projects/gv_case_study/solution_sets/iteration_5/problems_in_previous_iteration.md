**problems**

1. what I'm doing now I feel there's a few gaps: A. I need to know that founders appeared in inference are removed from the training set. B. I need to know founders with company that appear in both inference and training set are removed. [done]

2. Right now I use the highest multiple and corresponding founded year to label a founder, with a few performance based features. Meaning that for a founder, I'm considering their performance prior to the year their best return company was founded and predicting whether they would be a good candidate to talk to. I think this actually works for new founders, because that's what we want to do - talk the the founder with highest return potential, right at this moment. This should stay. [done]

3. iteration 4 did not include experience features. These should be aggregated from founder_experience and placed in feature_factory, attached after split.
- include experience features like
  - number of previous
    - c_suite roles (sum(is_c_suite))
    - employee roles (sum(is_employee))
    - executive roles (sum(is_executive))
    - founder roles (sum(is_founder))
    - board roles (sum(is_board))
  - total duration of experience (sum of all applicable duration where start and end date are present)
  - number of previous experiences

All of these are going to be added in feature_factory, and should consider cut_off_year.