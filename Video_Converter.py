import yt_dlp, json
import os, requests 
from moviepy.video.io.VideoFileClip import VideoFileClip
from dotenv import load_dotenv
import tempfile

load_dotenv("key.env")
API_KEY = os.getenv("API_KEY")
API_ENDPOINT = os.getenv("API_ENDPOINT")


# setup Jasper API
def setup_jasper_api_header():
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json" 
    }
    return headers

# Next setup the mutipart form data for the video file
def setup_jasper_api_form_data(file):
    processed_file = open(file, 'rb')
    # Jasper API requires name to be 100 characters or less
    file_name = os.path.basename(file)
    if len(file_name) > 100:
        name, ext = os.path.splitext(file_name)
        file_name = name[:100 - len(ext)] + ext
    form_data = {
        "name": (None, file_name),
        "file": (os.path.basename(file), processed_file, "audio/mpeg"),
        "settings":(None, json.dumps({"appVisibility": "visible", "autoSummary": True})),
        "tags": (None, "video_converter_app")
    }
    return form_data

# call API
def call_jasper_api(file):
    url = API_ENDPOINT
    headers = setup_jasper_api_header()
    form_data = setup_jasper_api_form_data(file)
    
    try:
        response = requests.post(url, headers=headers, files=form_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")  # Always log the response body for debugging
        response.raise_for_status()  # Check for HTTP errors
        print("API call successful!")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")

    finally:
        form_data["file"][1].close()  # Close the file after the request is done


def direct_youtube_video_download(video_url, output_dir=None):
    try:
        # Get video info first
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get('title', 'No Title')

        # Sanitize title for use as filename
        safe_title = "".join(c for c in video_title if c.isalnum() or c in " _-").strip()

        # Use a temp directory if none provided
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        full_path = os.path.join(output_dir, f"{safe_title}.mp4")

        # Download the video
        ydl_opts = {
            'format': '18',
            'outtmpl': full_path,
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl_dl:
            ydl_dl.download([video_url])

        return full_path, video_title
    except Exception as e:
        print(f"Error occurred: {e}")
        return None, None

# download the youtube video and save it 
def download_youtube_video(video_url, output_path=".", filename="downloaded_video.mp4") -> str:
    try:
        # First, get video info to extract title
        ydl_info = {
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_info) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get('title', 'No Title')
        
        # Create folder with video title
        video_folder = os.path.join(output_path, "video-audio-folder")
        os.makedirs(video_folder, exist_ok=True)
        
        # Full file path with title as filename
        full_path = os.path.join(video_folder, f"{video_title}.mp4")
        
        print(f"Downloading: {video_title}")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': '18',  # Format code 18 is 360p mp4 (low quality, widely compatible)
            'outtmpl': full_path,
            'quiet': False,
            'no_warnings': False,
        }
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return full_path
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def convert_video_to_mp3(file, output_folder=None) -> str:
    try:
        # Load the video file
        video_clip = VideoFileClip(file)
        
        # Define the output mp3 file name
        base_name = os.path.splitext(os.path.basename(file))[0] + '.mp3'
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
            mp3_file = os.path.join(output_folder, base_name)
        else:
            mp3_file = os.path.splitext(file)[0] + '.mp3'
        
        # Extract audio and write to mp3
        video_clip.audio.write_audiofile(mp3_file)

        # close the video clip to release resources
        video_clip.close()
        
        print(f"Conversion complete! MP3 file saved as: {mp3_file}")
        return mp3_file
    except Exception as e:
        print(f"Error occurred during conversion: {e}")
        return None



# Example usage:
def main():
    print("Choose an option:")
    print("1. Download from YouTube and convert")
    print("2. Convert local MP4 file to MP3")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        video_url_input = input("Enter the YouTube video URL: ")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mp4_video = download_youtube_video(video_url_input, output_path=script_dir)
        if mp4_video:
            mp3_audio = convert_video_to_mp3(mp4_video)
            if mp3_audio:
                call_jasper_api(mp3_audio)
            else:
                print("Failed to convert video to MP3.")
    
    elif choice == "2":
        mp4_file_path = input("Enter the full path to your MP4 file: ").strip().strip('"').strip("'")
        if os.path.exists(mp4_file_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            video_folder = os.path.join(script_dir, "video-audio-folder")
            mp3_audio = convert_video_to_mp3(mp4_file_path, output_folder=video_folder)
            if mp3_audio:
                call_jasper_api(mp3_audio)
            else:
                print("Failed to convert video to MP3.")
        else:
            print(f"File not found: {mp4_file_path}")
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()