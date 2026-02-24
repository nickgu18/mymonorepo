Direct ranking with LLMs is unlikly to work because of the non-deterministic nature of the token prediction.

Some enhanced ideas include confidence based majority vote, Pairwise Ranking Prompting (this is extened to be the founder arena idea).

majority vote largely resembles the deep think pipeline used by gpt 5 pro and gemini deep think.

For each founder, we ask LLM to predict the outcome class of these founders based on a set of foudner properties:

```markdown
**founder_properties**
1. career experience
2. prevvious company performance
3. network analysis
4. education history
5. personality traits (analyze from social media, categorize using Merrill-Reid Social Personality Styles, i.e driver, analytical, expressive, amiable)
6. previous failures, i.e number of failed startups
7. expertise domain (not just from education, maybe infer this from their publications, blogs)
8. current startup domain if any

**contact priority**
1-10, 1 being 'very low', 10 being 'talk now'

**task**
Given founder X and @founder_properties, predict the contact priority of founder X.

**example output**
contact priority: 4
explanation: why this founder should be contacted at priority 4
```

Then each LLM call aims to predict the contact priority of each founder.

For each founder we can do 5-10 calls in parallel and get the majority vote of the contact priority.

evaluation can be then done with the NDCG (we've got rank based on priority) as well as recall.