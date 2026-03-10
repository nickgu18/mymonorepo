#!/bin/bash
CONTENT=$(cat /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step2_plan.md)
gemini -y -p "Add comment to bug 490147352:
${CONTENT}"
