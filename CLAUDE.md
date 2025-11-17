# Countdown Audio Builder Project

This project contains Python scripts for generating spoken countdown audio files with beeps and rest prompts.

## Main Files
- `countdown_builder.py`: The main CLI script for building countdown audio
- `countdown_gui.py`: GUI interface for easy configuration and generation
- `countdown_web.py`: Web-based interface accessible via browser

## Dependencies
The script requires:
- `gtts` (Google Text-to-Speech)
- `pydub` (Audio manipulation)
- `ffmpeg` (Required by pydub for audio processing)

## Modes

### Numbers Mode (default)
Counts down repetitions: "40... 39... 38..."
Perfect for: Fitness, reps, exercise routines

### Minutes Mode (NEW)
Time-based countdown: "30 minutes remaining... 25 minutes remaining..."
Perfect for: Timers, Pomodoro, cooking, meditation, meetings

## Usage

### CLI
```bash
# Numbers mode (reps)
python countdown_builder.py --start 40 --outfile 40_reps.mp3

# Minutes mode with specific speaking times
python countdown_builder.py --mode minutes --start 30 --speak-at "30,15,10,5,1" --outfile timer.mp3

# Minutes mode speaking every 5 minutes
python countdown_builder.py --mode minutes --start 60 --speak-interval 5 --outfile 60min.mp3
```

See `examples.sh` for more usage patterns.

### GUI
Run the GUI with:
```bash
python countdown_gui.py
```

### Web Interface
Run the web interface with:
```bash
python countdown_web.py
```
Then open http://localhost:8001 in your browser.

## Key Features
- **Dual modes**: Numbers (reps) or Minutes (time-based)
- **Flexible speaking**: Every N minutes, or specific minutes only
- **Multi-language**: 40+ languages via Google TTS
- **Rest prompts**: Automatic rest cues at intervals
- **Customizable audio**: Beep frequency, duration, volume
- **TTS caching**: Fast regeneration
- **Timeline export**: JSON with precise timestamps
- **Multiple interfaces**: CLI, GUI, web
- **Preset management**: Save/load configurations

## Files
- `countdown_builder.py`: Main CLI script
- `countdown_gui.py`: GUI interface (tkinter)
- `countdown_web.py`: Web interface (built-in server)
- `examples.sh`: Example usage patterns
- `README.md`: Comprehensive documentation
- `CHANGELOG.md`: Version history and changes
- `requirements.txt`: Python dependencies
- `LICENSE`: MIT License