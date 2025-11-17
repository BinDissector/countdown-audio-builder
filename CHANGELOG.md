# Changelog

## Version 2.0.0 - Minutes Mode Update

### New Features

#### Minutes Mode
- **New countdown mode**: Added `--mode minutes` for time-based countdowns
- Speaks remaining minutes instead of rep numbers
- Perfect for timers, productivity tools, cooking, meditation, etc.

#### Flexible Speaking Options
- **`--speak-interval N`**: Speak only every N minutes (e.g., every 5 minutes)
- **`--speak-at "M1,M2,M3..."`**: Speak only at specific minutes (e.g., "30,15,10,5,1")
- **`--minute-text "text"`**: Customize the spoken text (default: "minutes remaining")
  - Automatically handles singular/plural (e.g., "1 minute remaining" vs "5 minutes remaining")

### Examples

```bash
# 30-minute Pomodoro timer
python countdown_builder.py --mode minutes --start 25 --speak-at "25,10,5,1" \
  --lead-in "Focus time begins" --end-with "Time for a break" --outfile pomodoro.mp3

# 60-minute timer speaking every 10 minutes
python countdown_builder.py --mode minutes --start 60 --speak-interval 10 \
  --outfile 60min_timer.mp3

# Custom timer with specific checkpoints
python countdown_builder.py --mode minutes --start 90 \
  --speak-at "90,60,45,30,15,10,5,1" --outfile 90min_custom.mp3
```

### Technical Changes

**countdown_builder.py:**
- Added `build_minutes_countdown()` function for minutes-based audio generation
- Added `should_speak_minute()` helper function
- Extended `Settings` dataclass with:
  - `mode`: "numbers" or "minutes"
  - `speak_interval`: Interval for speaking (minutes mode)
  - `speak_at`: List of specific minutes to speak
  - `minute_text`: Customizable text appended to minute count
- Updated CLI argument parser with new options
- Modified `main()` to select appropriate builder based on mode

**README.md:**
- Updated feature list to highlight dual modes
- Added comprehensive examples for both modes
- Reorganized use cases by mode
- Added Minutes Mode examples section

**New Files:**
- `examples.sh`: Shell script with example usage patterns
- `CHANGELOG.md`: This file

### Backwards Compatibility

All existing functionality is preserved. The default mode is "numbers" (rep counting), so existing commands work exactly as before.

---

## Version 1.0.0 - Initial Release

### Features
- Numbers-based countdown (rep counting)
- Customizable beeps and intervals
- Rest prompts at configurable intervals
- Multi-language TTS support
- Timeline JSON export
- CLI, GUI, and web interfaces
- TTS caching for performance
