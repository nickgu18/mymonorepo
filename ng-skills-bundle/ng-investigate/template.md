# Mission Order Template


## Order (fill every field — mark N/A if not applicable)


**Intent:** Why we're doing this and the desired end state.


**Constraints:** Forbidden actions.


**Done-when:** Verifiable success criteria.


**Resources:** Access, paths, context the agent needs.


**ROE:** Read-only / write / deploy. What requires approval.


**Handoff:** Return format below — no freeform.


## Handoff Schema


```
status:      complete | blocked | partial
result:      what was done
artifacts:   [files, URLs, outputs]
deviations:  [departures from plan + why]
concerns:    [risks, unknowns]
```
