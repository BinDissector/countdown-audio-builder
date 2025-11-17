#!/bin/bash
# Example usage of countdown_builder.py

## Minutes Mode Examples

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

## Numbers Mode Examples

# Example 4: Traditional rep countdown with rest every 10
python3 countdown_builder.py --start 50 --every-n 10 \
  --outfile 50_reps.mp3

# Example 5: Custom rest text - short phrase
python3 countdown_builder.py --start 40 --every-n 8 \
  --rest-text "take a brief pause" \
  --outfile 40_custom_rest.mp3

# Example 6: Custom rest text - motivational
python3 countdown_builder.py --start 100 --every-n 20 \
  --rest-text "breathe and recover" \
  --lead-in "Let's begin the workout" \
  --end-with "Amazing job! You did it" \
  --outfile 100_motivational.mp3

# Example 7: Multi-language with custom rest
python3 countdown_builder.py --start 30 --every-n 10 \
  --lang es --rest-text "toma un descanso" \
  --outfile 30_spanish_rest.mp3
