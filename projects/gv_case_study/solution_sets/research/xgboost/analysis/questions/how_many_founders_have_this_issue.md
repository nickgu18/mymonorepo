success criteria of answers: comprehensive, and also include a ELI5 section for beginners.

Question:

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

Analysis:

Conclusion:
