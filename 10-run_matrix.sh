#!/bin/sh
# Runs the same questions through: before (original code), and after with A only, B only, A+B.
# Greedy decoding so a re-run gives the same text. Needs the venv from README.
cd "$(dirname "$0")"; mkdir -p results
export DEMO_GREEDY=1 DEMO_MAX_NEW_TOKENS=220
A_ON="G_A1_CLEAN_SCRAPE=1 G_A2_RELEVANCE_BAR=1"; A_OFF="G_A1_CLEAN_SCRAPE=0 G_A2_RELEVANCE_BAR=0"
B_ON="G_B1_PROMPT_SEPARATION=1 G_B2_SAFE_RENDER=1 G_B3_INPUT_LIMITS=1 G_B4_SAFE_ERRORS=1 G_B5_WEAK_SIGNAL_LOGS=1"
B_OFF="G_B1_PROMPT_SEPARATION=0 G_B2_SAFE_RENDER=0 G_B3_INPUT_LIMITS=0 G_B4_SAFE_ERRORS=0 G_B5_WEAK_SIGNAL_LOGS=0"
run() { [ -s results/$1.json ] && return 0
  env $3 ${5:+DEMO_EXTRA_DOCS=$5} python engine_run.py $2 $4 results/$1.json > results/$1.log 2>&1
}
for set in main poison; do
  Q=tests/questions_$set.json; X=""; [ $set = poison ] && X=tests/poisoned_doc.json
  run ${set}_1_before before "" $Q $X
  run ${set}_2_A_only after "$A_ON $B_OFF" $Q $X
  run ${set}_3_B_only after "$A_OFF $B_ON" $Q $X
  run ${set}_4_A_plus_B after "$A_ON $B_ON" $Q $X
done
# fidelity check: 'after' with every flag off should behave like 'before'
run fidelity_after_all_off after "$A_OFF $B_OFF" tests/questions_main.json
echo ALLDONE > results/DONE
