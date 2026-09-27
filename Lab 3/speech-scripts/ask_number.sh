#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "Hi Bowei. How many pets do you have? Please answer after the question." |
  python3 -m piper -m en_US-lessac-medium --output_file /tmp/ask_number_question.wav
aplay /tmp/ask_number_question.wav

echo "Recording your answer for 5 seconds..."
arecord -d 5 -f cd -c 1 -r 16000 number_answer.wav
echo "Saved your answer to number_answer.wav"
