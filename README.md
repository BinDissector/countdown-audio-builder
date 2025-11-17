# Countdown Audio Builder

A powerful Python tool for generating customizable spoken countdown audio files with beeps and rest prompts. Perfect for workout routines, interval training, timed exercises, timers, or any activity requiring spoken time tracking.

## Features

- **Dual Modes**:
  - **Numbers Mode**: Count down reps (e.g., "40, 39, 38...")
  - **Minutes Mode**: Time-based countdown (e.g., "30 minutes remaining")
- **Flexible Speaking Options**:
  - Speak at specific intervals (e.g., every 5 minutes)
  - Speak only at specific times (e.g., 30, 15, 10, 5, 1)
  - Full customization of spoken text
- **Spoken Countdown**: Text-to-speech using Google TTS with 40+ language support
- **Customizable Intervals**: Configure timing between counts and rest periods
- **Rest Prompts**: Automatic rest cues at configurable intervals (numbers mode only)
- **Beep Sounds**: Adjustable frequency, duration, and volume
- **Distinctive End Beep**: Longer, higher-pitched beep signals countdown completion
- **TTS Caching**: Speeds up regeneration by caching voice files
- **Timeline Export**: JSON timeline for editing in external tools
- **Multiple Interfaces**: Command-line, GUI, and web-based interfaces
- **Preset Management**: Save and load configurations for different workout types
- **High-Quality Audio**: MP3 export with adjustable bitrate

## Installation

### Prerequisites

- Python 3.7 or higher
- ffmpeg (required for audio processing)
- python3-tk (required for GUI interface)

#### Installing Dependencies

**Ubuntu/Debian/Pop!_OS:**
```bash
sudo apt update
sudo apt install -y ffmpeg python3-tk
```

**macOS (with Homebrew):**
```bash
brew install ffmpeg
# tkinter is included with Python on macOS
```

**Windows:**
- Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- tkinter is included with Python on Windows

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install gtts pydub
```

**Note:** The GUI requires `python3-tk` which must be installed via your system package manager (see above).

## Usage

### Command Line Interface

The most flexible way to generate countdown audio:

**Numbers Mode (default):**
```bash
python countdown_builder.py --start 40 --interval 3.5 --outfile 40_reps.mp3
```

**Minutes Mode:**
```bash
python countdown_builder.py --mode minutes --start 30 --speak-at "30,15,10,5,1" --outfile 30min_timer.mp3
```

#### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Countdown mode: "numbers" or "minutes" | numbers |
| `--start` | Starting number (reps or minutes) | 80 |
| `--interval` | Seconds between normal cues | 3.5 |
| `--long-interval` | Seconds after rest cues | 8.0 |
| `--every-n` | Insert rest every N counts (0 to disable) | 8 |
| `--skip-first-rest` | Skip first N rest periods | 0 |
| `--speak-interval` | (Minutes mode) Speak every N minutes (0 = all) | 0 |
| `--speak-at` | (Minutes mode) Speak at specific minutes (e.g., "30,15,10,5,1") | None |
| `--minute-text` | (Minutes mode) Text to append to minute count | "minutes remaining" |
| `--lead-in` | Opening phrase (e.g., "Get ready") | None |
| `--end-with` | Closing phrase (e.g., "Good job!") | None |
| `--rest-text` | Word spoken at rest cues | "rest" |
| `--lang` | Language code (en, es, fr, de, etc.) | en |
| `--tld` | Voice region (com, co.uk, com.au, etc.) | com |
| `--outfile` | Output MP3 filename | countdown_combined.mp3 |
| `--out-bitrate` | MP3 bitrate (128k, 192k, 256k, 320k) | 192k |
| `--beep-freq` | Beep frequency in Hz | 1000 |
| `--beep-ms` | Beep duration in milliseconds | 300 |
| `--beep-gain` | Beep volume in dB (negative = quieter) | -6.0 |

#### Examples

**Numbers Mode Examples:**

**Basic 40-rep countdown:**
```bash
python countdown_builder.py --start 40 --outfile 40_reps.mp3
```

**Spanish countdown with custom rest text:**
```bash
python countdown_builder.py --start 30 --lang es --rest-text "descanso"
```

**HIIT workout with lead-in and ending:**
```bash
python countdown_builder.py --start 60 --every-n 10 --lead-in "Get ready to begin" --end-with "Great work!"
```

**Skip warmup rests:**
```bash
python countdown_builder.py --start 50 --every-n 10 --skip-first-rest 2
```

**Minutes Mode Examples:**

**30-minute timer speaking every 5 minutes:**
```bash
python countdown_builder.py --mode minutes --start 30 --speak-interval 5 --outfile 30min_timer.mp3
```

**60-minute timer speaking at specific times:**
```bash
python countdown_builder.py --mode minutes --start 60 --speak-at "60,45,30,15,10,5,1" --outfile 60min_custom.mp3
```

**25-minute Pomodoro timer:**
```bash
python countdown_builder.py --mode minutes --start 25 --speak-at "25,10,5,1" \
  --lead-in "Focus time begins now" --end-with "Time for a break" --outfile pomodoro.mp3
```

**Custom minute text (e.g., in Spanish):**
```bash
python countdown_builder.py --mode minutes --start 20 --speak-interval 5 \
  --lang es --minute-text "minutos restantes" --outfile 20min_spanish.mp3
```

**Silent timer (beeps only at specific minutes):**
```bash
python countdown_builder.py --mode minutes --start 15 --speak-at "15,1" \
  --beep-freq 800 --beep-ms 500 --outfile silent_timer.mp3
```

### Graphical User Interface

For an easy-to-use visual interface:

```bash
python countdown_gui.py
```

The GUI provides:
- Organized tabs for Basic, Advanced, and Audio settings
- Real-time progress tracking
- Audio preview functionality
- Save/load preset configurations
- File browser for output selection

### Web Interface

For browser-based access:

```bash
python countdown_web.py
```

Then open http://localhost:8001 in your browser. Features:
- Works on any device with a browser
- No GUI libraries required
- Download generated files
- Save/load presets as JSON files

## Output Files

Each generation creates two files:

1. **MP3 Audio File**: The complete countdown audio (e.g., `countdown_combined.mp3`)
2. **Timeline JSON**: Detailed cue timing for editing (e.g., `countdown_combined.json`)

### Timeline Format

The JSON timeline contains precise timestamps for each audio element:

```json
[
  {
    "label": "Get ready",
    "start": 0,
    "end": 1523
  },
  {
    "label": "40",
    "start": 2523,
    "end": 3012
  }
]
```

Times are in milliseconds. Use this for:
- Editing in audio software
- Syncing with video
- Creating visual countdown displays
- Custom integration into apps

## Use Cases

### Numbers Mode (Rep Counting)
- **Fitness Training**: HIIT workouts, rep counting, timed exercises
- **Physical Therapy**: Structured exercise routines with rest periods
- **Sports Coaching**: Drill timing, interval training

### Minutes Mode (Time-Based)
- **Productivity**: Pomodoro technique (25-minute work blocks), focus timers
- **Cooking**: Long-duration recipes, slow cooking, proofing timers
- **Educational**: Test duration, exam timers, study sessions
- **Presentations**: Speaker time limits, presentation countdowns
- **Meditation**: Guided meditation sessions with interval bells
- **Parking Meters**: Remind you when time is running out
- **Household Tasks**: Laundry timers, cleaning routines
- **Meetings**: Keep meetings on track with time reminders

## Advanced Features

### TTS Caching

Generated voice files are cached in `tts_cache/` directory. This means:
- Faster regeneration when reusing numbers
- Reduced API calls to Google TTS
- Delete the cache folder to refresh voices

### Multi-Language Support

Supports all Google TTS languages including:
- English (en), Spanish (es), French (fr)
- German (de), Italian (it), Portuguese (pt)
- Japanese (ja), Chinese (zh), Korean (ko)
- And many more

Use `--lang` and `--tld` to customize voice accent:
```bash
python countdown_builder.py --lang en --tld co.uk  # British English
python countdown_builder.py --lang en --tld com.au  # Australian English
```

## Troubleshooting

### "No module named 'tkinter'" Error

**Linux/Ubuntu/Pop!_OS:**
```bash
sudo apt update
sudo apt install -y python3-tk
```

**macOS/Windows:** tkinter is included with Python, no action needed.

### "pydub/ffmpeg not ready" Error

Make sure ffmpeg is installed and accessible in your PATH:
```bash
# Test if ffmpeg is installed
ffmpeg -version
```

If not found, install it:
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### TTS Failures

- Check your internet connection (Google TTS requires internet)
- The script automatically retries failed TTS calls
- Network issues may cause temporary failures

### Audio Quality Issues

- Increase `--out-bitrate` for better quality (e.g., 320k)
- Adjust `--beep-gain` if beeps are too loud/quiet
- Modify `--fade-ms` to reduce audio clicks

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Author

Created with Claude Code

## Acknowledgments

- Uses [gTTS](https://github.com/pndurette/gTTS) for text-to-speech
- Uses [pydub](https://github.com/jiaaro/pydub) for audio manipulation
- Requires [ffmpeg](https://ffmpeg.org/) for audio processing
