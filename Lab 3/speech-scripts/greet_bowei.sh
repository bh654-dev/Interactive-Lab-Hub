#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Hi Bowei, welcome back! Hope you have a great day." |
  python3 -m piper -m en_US-lessac-medium --output_file /tmp/greet_bowei.wav
aplay /tmp/greet_bowei.wav
