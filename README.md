# Countdown Audio Builder

A powerful Python tool for generating customizable spoken countdown audio files with beeps and rest prompts. Perfect for workout routines, interval training, timed exercises, or any activity requiring spoken time tracking.

## Features

- **Spoken Countdown**: Text-to-speech countdown using Google TTS with multiple language support
- **Customizable Intervals**: Configure timing between counts and rest periods
- **Rest Prompts**: Automatic rest cues at configurable intervals
- **Beep Sounds**: Adjustable frequency, duration, and volume
- **TTS Caching**: Speeds up regeneration by caching voice files
- **Timeline Export**: JSON timeline for editing in external tools
- **Multiple Interfaces**: Command-line, GUI, and web-based interfaces
- **Preset Management**: Save and load configurations for different workout types
- **High-Quality Audio**: MP3 export with adjustable bitrate

## Installation

### Prerequisites

- Python 3.7 or higher
- ffmpeg (required for audio processing)

#### Installing ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS (with Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install gtts pydub
```

## Usage

### Command Line Interface

The most flexible way to generate countdown audio:

```bash
python countdown_builder.py --start 40 --interval 3.5 --long-interval 8 --every-n 8
```

#### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--start` | Starting number for countdown | 80 |
| `--interval` | Seconds between normal cues | 3.5 |
| `--long-interval` | Seconds after rest cues | 8.0 |
| `--every-n` | Insert rest every N counts (0 to disable) | 8 |
| `--skip-first-rest` | Skip first N rest periods | 0 |
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

- **Fitness Training**: HIIT workouts, rep counting, timed exercises
- **Physical Therapy**: Structured exercise routines with rest periods
- **Sports Coaching**: Drill timing, interval training
- **Presentations**: Speaker countdowns
- **Cooking**: Timed recipe steps
- **Educational**: Classroom timers, test countdowns
- **Productivity**: Pomodoro technique, work intervals

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

### "pydub/ffmpeg not ready" Error

Make sure ffmpeg is installed and accessible in your PATH.

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
