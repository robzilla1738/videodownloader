import os
import subprocess
import requests
from pathlib import Path
from urllib.parse import urljoin

def fetch_m3u8_playlist(m3u8_url):
    """
    Fetch the master .m3u8 playlist to ensure the highest quality is downloaded.
    """
    try:
        response = requests.get(m3u8_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        content = response.text

        # Check if it's a master playlist (contains other .m3u8 links)
        if "#EXT-X-STREAM-INF" in content:
            lines = content.splitlines()
            for line in lines:
                if line.endswith(".m3u8"):
                    # Return the first (typically highest quality) .m3u8 link
                    return urljoin(m3u8_url, line)
        else:
            # Return the provided .m3u8 if it's a single stream
            return m3u8_url
    except Exception as e:
        print(f"Error fetching m3u8 playlist: {e}")
        return None

def download_highest_quality_video(video_url, save_path="./downloads", output_file="output.mp4"):
    """
    Downloads the highest quality video using ffmpeg from a provided video URL (e.g., .m3u8).
    """
    try:
        os.makedirs(save_path, exist_ok=True)
        output_path = os.path.join(save_path, output_file)

        # Fetch the highest quality stream if it's an m3u8 file
        if video_url.endswith(".m3u8"):
            video_url = fetch_m3u8_playlist(video_url)

        if not video_url:
            print("Could not fetch a valid video URL.")
            return

        # Run ffmpeg command to download and merge the best quality video and audio
        print(f"Downloading video from: {video_url}")
        command = [
            "ffmpeg",
            "-i", video_url,  # Input URL
            "-c", "copy",  # Copy without re-encoding
            "-map", "0:v:0",  # Select the best video stream
            "-map", "0:a:0",  # Select the best audio stream
            output_path
        ]
        subprocess.run(command, check=True)
        print(f"Download completed: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Highest Quality Video Downloader")
    print("=" * 40)

    # Input the video URL
    video_url = input("Enter the video URL (.m3u8 or direct): ").strip()
    if not video_url:
        print("Error: No video URL provided.")
        exit()

    # Input save directory and output file name
    save_path = input("Enter the directory to save the file (default: ./downloads): ").strip() or "./downloads"
    output_file = input("Enter the output file name (default: output.mp4): ").strip() or "output.mp4"

    # Download the video
    download_highest_quality_video(video_url, save_path, output_file)
