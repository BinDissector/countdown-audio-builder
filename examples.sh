#!/bin/bash
# Example usage of countdown_builder.py with minutes mode

# Example 1: 30-minute timer speaking every 5 minutes
python3 countdown_builder.py --mode minutes --start 30 --speak-interval 5 \
  --outfile 30min_every5.mp3

# Example 2: 60-minute timer speaking at specific times
python3 countdown_builder.py --mode minutes --start 60 \
  --speak-at "60,45,30,15,10,5,1" \
  --outfile 60min_specific.mp3

# Example 3: 20-minute Pomodoro timer
python3 countdown_builder.py --mode minutes --start 20 \
  --speak-at "20,10,5,1" \
  --lead-in "Focus time begins now" \
  --end-with "Great work! Take a break" \
  --outfile pomodoro.mp3

# Example 4: Traditional rep countdown (numbers mode - default)
python3 countdown_builder.py --start 50 --every-n 10 \
  --outfile 50_reps.mp3
