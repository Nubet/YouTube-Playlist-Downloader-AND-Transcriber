## YouTube Playlist Downloader & Transcriber

This projects combine `yt_dlp` and `Vosk` to download all videos from a YouTube playlist or channel URL and transcribe any videos that don’t already have a transcript.

---

### Features

- **Download missing videos**: Uses `yt_dlp`’s `download_archive` to skip already-downloaded videos.
- **Multiple formats**: Downloads best available video and audio.
- **Offline transcription**: Processes each video with **Vosk** and `ffmpeg` to produce `.txt` transcripts.
- **Idempotent**: Won’t re-download or re-transcribe existing files.

---

## Prerequisites

1. **Python 3.8+**
2. **ffmpeg** installed and available on your system `PATH`.
3. **yt_dlp** Python package:
   ```bash
   pip install yt_dlp
   ```
4. **vosk** Python package and a local Vosk model (e.g., [vosk-model-small-en-us-0.15]).
   ```bash
   pip install vosk tqdm
   ```
   Download a model:
   ```bash
   # Example: 
   small model - https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   medium model - https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
 
   ```

---

## Installation

1. Clone or download this repository.
2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

```bash
python main.py   --url "<PLAYLIST_OR_CHANNEL_URL>"   --download-dir "/path/to/videos"   --archive "/path/to/yt_archive.txt"   --model-dir "/path/to/vosk-model"   [--transcript-dir "/path/to/transcripts"]
```

| Option            | Description                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| `-u`, `--url`     | **Required.** YouTube playlist or channel URL.                                               |
| `-d`, `--download-dir` | Directory where videos are saved (default: `~/Downloads`).                               |
| `-a`, `--archive` | Path to the download archive file (tracks completed IDs, default: `~/yt_archive.txt`).        |
| `-m`, `--model-dir` | **Required.** Local Vosk model directory.                                                   |
| `-t`, `--transcript-dir` | Directory to output transcripts (defaults alongside videos).                            |

**Example:**
```bash
python .\main.py `
  --url "https://www.youtube.com/playlist?list=PLA1FTfKBAEX4hblYoH6mnq0zsie2w6Wif" `
  --download-dir "C:/MOVIES" `
  --model-dir "C:/vosk-model-small-en-us-0.15" `
  --transcript-dir "C:/MOVIES/transcripts"
```

---

## How It Works

1. **Download Stage**:
   - The script invokes `yt_dlp` with `--download_archive` so already-downloaded video IDs are listed in the archive and skipped on subsequent runs.
   - Videos are saved by their YouTube ID and original extension into the download directory.
2. **Transcript Stage**:
   - Loads the Vosk model and transcribes each video via `ffmpeg` to mono 16 kHz WAV streams.
   - Only generates `.txt` if none exists for the video ID.

---

## Troubleshooting

- **No videos downloaded**: Check your `--url` is correct and not private.
- **ffmpeg not found**: Ensure `ffmpeg` is installed and in your `PATH`.
- **Vosk errors**: Verify the `--model-dir` points to a valid Vosk model folder.

---

## License

MIT LICENSE
