# Countdown Audio Builder Project

This project contains a Python script for generating spoken countdown audio files with beeps and rest prompts.

## Main File
- `countdown_builder.py`: The main Python script for building countdown audio

## Dependencies
The script requires:
- `gtts` (Google Text-to-Speech)
- `pydub` (Audio manipulation)
- `ffmpeg` (Required by pydub for audio processing)

## Usage
Run the script with various options to customize your countdown audio. See the script's help for all available options:
```bash
python countdown_builder.py --help
```

## Files
- `countdown_builder.py`: The main Python script for building countdown audio
- `countdown_gui.py`: GUI interface for easy configuration and generation

## Features
- Spoken countdown with configurable start number
- Beeps between numbers
- Rest prompts at configurable intervals
- Caching for TTS to speed up repeated runs
- Timeline JSON output for editing
- MP3 output with configurable bitrate
- **NEW**: Easy-to-use GUI with organized tabs for settings
- **NEW**: Progress tracking during generation
- **NEW**: Audio preview functionality
- **NEW**: Save/load presets for different workout types

## GUI Usage
Run the GUI with:
```bash
python countdown_gui.py
```

The GUI provides:
- **Basic Settings**: Core countdown parameters
- **Advanced Settings**: Text and language options  
- **Audio Settings**: Beep and audio processing controls
- **Generate Button**: Creates the countdown with progress tracking
- **Preview Button**: Plays the generated audio file
- **Preset Management**: Save and load configuration presets