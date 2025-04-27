import os
import sys
import argparse
import subprocess
from glob import glob
from tqdm import tqdm
import json
import yt_dlp
from vosk import Model, KaldiRecognizer

def download_videos(playlist_url, download_dir, archive_file, use_ids, extension):
    """
    Download videos from a YouTube playlist, skipping those already downloaded.
    Uses yt_dlp's download_archive to track completed downloads.
    Returns a list of video file paths present in download_dir after run.
    """
    os.makedirs(download_dir, exist_ok=True)

    # choose filename template based on user preference
    template = '%(id)s.%(ext)s' if use_ids else '%(title)s.%(ext)s'

    # build yt_dlp format string and optional merge_output_format
    ydl_opts = {
        'outtmpl': os.path.join(download_dir, template),
        'restrictfilenames': True,
        'noplaylist': False,
        'download_archive': archive_file,
        'ignoreerrors': True,
        'quiet': True,
    }

    # for mp4/webm we can force container via format string
    if extension in ('mp4', 'webm', 'flv'):
        # choose audio ext for mp4
        audio_ext = 'm4a' if extension == 'mp4' else extension
        ydl_opts['format'] = f'bestvideo[ext={extension}]+bestaudio[ext={audio_ext}]/{extension}'
    else:
        # letting yt-dlp pick best streams, and then merge into given container
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = extension  # e.g. "mkv"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    # collect all video files with the requested extension
    video_paths = []
    for ext in (extension,):
        video_paths.extend(glob(os.path.join(download_dir, f"*.{ext}")))
    return video_paths

def transcribe_video(model, video_path, txt_path):
    """
    Transcribe a single video file to text using Vosk.
    """
    cmd = [
        'ffmpeg', '-loglevel', 'quiet', '-i', video_path,
        '-ar', '16000', '-ac', '1', '-f', 'wav', 'pipe:1'
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)

    with open(txt_path, 'w', encoding='utf-8') as f:
        while True:
            data = proc.stdout.read(4000)
            if not data:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get('text', '').strip()
                if text:
                    f.write(text + '\n')
        final = json.loads(rec.FinalResult())
        text = final.get('text', '').strip()
        if text:
            f.write(text + '\n')

def transcribe_videos(video_files, model_path, out_dir=None):
    """
    Transcribe all videos in the list without existing transcripts.
    """
    if not os.path.isdir(model_path):
        print(f"Vosk model not found at: {model_path}", file=sys.stderr)
        sys.exit(1)
    model = Model(model_path)

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    for video in tqdm(video_files, desc="Transcribing videos"):
        base = os.path.splitext(os.path.basename(video))[0]
        txt_name = base + '.txt'
        txt_path = os.path.join(out_dir or os.path.dirname(video), txt_name)
        if os.path.exists(txt_path):
            continue
        try:
            transcribe_video(model, video, txt_path)
        except Exception as e:
            print(f"Error transcribing {video}: {e}", file=sys.stderr)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Download & transcribe YouTube playlist offline with Vosk"
    )
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='YouTube playlist or channel URL'
    )
    parser.add_argument(
        '-d', '--download-dir',
        default=os.path.join(os.path.expanduser('~'), 'Downloads'),
        help='Directory to save videos'
    )
    parser.add_argument(
        '-a', '--archive',
        default=os.path.join(os.path.expanduser('~'), 'yt_archive.txt'),
        help='Path to download archive file'
    )
    parser.add_argument(
        '-m', '--model-dir',
        required=True,
        help='Path to Vosk model'
    )
    parser.add_argument(
        '-t', '--transcript-dir',
        default=None,
        help='Directory to save transcripts'
    )
    parser.add_argument(
        '--use-ids',
        action='store_true',
        help='Save downloaded videos using their YouTube IDs instead of titles'
    )
    parser.add_argument(
        '-e', '--extension',
        choices=['mp4', 'webm', 'mkv', 'flv'],
        default='mp4',
        help='Desired video container extension (affects download format/merging)'
    )
    return parser.parse_args()

def main():
    args = parse_args()

    print("Downloading videos...")
    videos = download_videos(
        args.url,
        args.download_dir,
        args.archive,
        args.use_ids,
        args.extension
    )
    print(f"Found {len(videos)} .{args.extension} video(s) in {args.download_dir}")

    print("Transcribing missing...")
    transcribe_videos(videos, args.model_dir, args.transcript_dir)
    print("Done.")

if __name__ == '__main__':
    main()
