#!/bin/bash
gemini -y -p "Add comment to bug 490147352 with the exact content of file: /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step2_plan.md" > /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/post_step2.log 2>&1 &

gemini -y -p "Add comment to bug 490147352 with the exact content of file: /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step3_plan.md" > /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/post_step3.log 2>&1 &

gemini -y -p "Add comment to bug 490147352 with the exact content of file: /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/step4_plan.md" > /usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/post_step4.log 2>&1 &

echo "Started background jobs to post comments."
