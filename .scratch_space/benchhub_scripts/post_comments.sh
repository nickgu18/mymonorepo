#!/bin/bash
step2=$(cat /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step2_plan.md)
step3=$(cat /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step3_plan.md)
step4=$(cat /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step4_plan.md)

gemini -y -p "Add comment to bug 490147352:
Plan for Step 2:

$step2"

gemini -y -p "Add comment to bug 490147352:
Plan for Step 3:

$step3"

gemini -y -p "Add comment to bug 490147352:
Plan for Step 4:

$step4"
