# YouTube Playlist Downloader & Transcriber

This project combines `yt_dlp`, `ffmpeg`, and `Vosk` to download all videos from a YouTube playlist or channel URL and transcribe any videos that don’t already have a transcript.

---

## Features

- **Download missing videos**: Skips already-downloaded entries via `yt_dlp`’s `download_archive`.
- **ID or title–based filenames**: Optionally save videos by YouTube ID (`--use-ids`) or by title.
- **Multiple container formats**: Supports `mp4`, `webm`, `mkv`, `flv` through format selection and merging.
- **Progress bar**: Displays transcription progress with `tqdm`.
- **Offline transcription**: Uses `Vosk` and `ffmpeg` to produce `.txt` transcripts.
- **Idempotent**: Won’t re-download or re-transcribe files that already exist.

---

## Prerequisites

1. **Python 3.8+**
2. **ffmpeg** installed and in your `PATH`.
3. A local Vosk model (e.g., [vosk-model-small-en-us-0.15]). Download from:
   ```bash
   https://alphacephei.com/vosk/models/
   ```

---

## Installation

1. Clone or download this repository.
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

```bash
python main.py   --url "<PLAYLIST_OR_CHANNEL_URL>"   --download-dir "/path/to/videos"   --archive "/path/to/yt_archive.txt"   --model-dir "/path/to/vosk-model"   [--transcript-dir "/path/to/transcripts"]   [--use-ids]   [--extension {mp4,webm,mkv,flv}]
```

| Option                  | Description                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `-u`, `--url`           | **Required.** YouTube playlist or channel URL.                                                                     |
| `-d`, `--download-dir`  | Directory where videos are saved (default: `~/Downloads`).                                                         |
| `-a`, `--archive`       | Path to download archive file tracking completed IDs (default: `~/yt_archive.txt`).                                |
| `-m`, `--model-dir`     | **Required.** Local Vosk model directory.                                                                           |
| `-t`, `--transcript-dir`| Directory to save transcripts (defaults alongside videos).                                                          |
| `--use-ids`             | Save downloaded videos using their YouTube IDs instead of titles.                                                   |
| `-e`, `--extension`     | Desired container extension `{mp4, webm, mkv, flv}` (default: `mp4`), affects download format/merging.             |

---

## Example

```bash
python .\main.py `
  --url "https://www.youtube.com/playlist?list=PLA1FTfKBAEX4hblYoH6mnq0zsie2w6Wif" `
  --download-dir "C:/MOVIES" `
  --model-dir "C:/vosk-model-small-en-us-0.15" `
  --transcript-dir "C:/MOVIES/transcripts" `
  --extension mkv
```

```

---

## How It Works

1. **Download Stage**
   - Builds `yt_dlp` options:
     - `outtmpl`: `%(id)s.%(ext)s` or `%(title)s.%(ext)s` based on `--use-ids`.
     - `download_archive`: tracks downloaded IDs to skip repeats.
     - `format` / `merge_output_format`: selects best streams by extension or merges into the chosen container.
   - Runs `yt_dlp.download()` on the provided URL.
   - Gathers all files matching the chosen extension in the download directory.

2. **Transcription Stage**
   - Verifies and loads the Vosk model directory.
   - For each video (skipping those with an existing `.txt`):
     - Pipes audio via `ffmpeg` to 16 kHz mono WAV.
     - Uses `KaldiRecognizer` with `SetWords(True)` for word-level timestamps.
     - Writes interim (`rec.AcceptWaveform`) and final (`rec.FinalResult`) results line-by-line into a `.txt`.
   - Progress is displayed via `tqdm`.

---

## Troubleshooting

- **No videos downloaded**: Check that your `--url` is correct and publicly accessible.
- **Unsupported extension**: Ensure `-e`/`--extension` is one of `mp4`, `webm`, `mkv`, or `flv`.
- **ffmpeg errors**: Confirm `ffmpeg` is installed and available on your `PATH`.
- **Vosk model not found**: Validate the `--model-dir` path; the script will exit with an error if the model is invalid.
- **Transcription failures**: Inspect stderr for messages like `Error transcribing <video>: <exception>` and verify audio input.

---

## License

MIT License
