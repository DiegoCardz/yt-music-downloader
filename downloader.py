#%% Get a youtube video from a url ando download it as m4a
import os
from yt_dlp import YoutubeDL
from metadata_deriver import derive_metadata


#%% Function to validate and format YouTube URL
def get_validated_url(url):
    # Get video ID from url
    video_id = url.split("v=")[-1]
    if "&" in video_id:
        video_id = video_id.split("&")[0]
    
    validated_url = f"https://www.youtube.com/watch?v={video_id}"
    return validated_url

#%% Function to print video information nicely
def print_video_info(info:dict, print_len:int=60, select_keys:bool=True) -> None:
    """Prints video information in a formatted way.
    Args:
        info (dict): 
            Dictionary containing video information.
        print_len (int): Optional. 
            Length of the printed line. 
            Default value is 80
        select_keys (bool): Optional. 
            Whether to print all keys or select keys only.
    """
    if select_keys:
        select_info_keys = {
            "id", "track", "title", "artist", "album", "year", "picture", 
            "url", 
        }
        info = {k:v for k,v in info.items() if k in select_info_keys}
    
    
    key_max_len = max(len(k) for k in info.keys())
    val_max_len = print_len-key_max_len-4
    print(f"{'┌─── Video Information: ─':─<{print_len}}─┐")
    for key, val in info.items():
        def print_ltd (x: str) -> str:
            x = x.replace("\n"," ")
            if len(x) <= val_max_len: return x  
            else: return x[:val_max_len-3] + "..."
        print(f"├ {key:<{key_max_len}}: "
            f"{print_ltd(str(val)):<{val_max_len}} │")
    print(f"{'└':─<{print_len}}─┘")

#%% Function to get video information
def get_video_info(url: str, ydl_opts: dict=None, derive_missing: bool=True) -> dict:
    """Get video information from YouTube URL using yt-dlp.
    Args:
        url (str): YouTube video URL
        ydl_opts (dict, optional): Optional dictionary with yt-dlp specifications.
        derive_missing (bool): Whether to derive missing metadata fields. 
            Defaults to True.
    Returns:
        dict: Dictionary containing video information
        
    """
    try: #Get info without downloading
        info = YoutubeDL(ydl_opts).extract_info(url, download=False)
        
        if derive_missing:
            info["url"] = url  # Ensure functional URL in metadata
            info = derive_metadata(info)

        return info
    except Exception as e:
        print(f"Error retrieving video info with yt-dlp: {e}")
        return {'0':None}

#%% Function to download audio from YouTube video
def download_M4A_audio(url:str, info:dict=None, output_path:str=None) -> str:
    """
    Download audio from YouTube video as M4A file.
    Args:
        url (str): YouTube video URL
        output_path (str, optional): 
            Directory to save the downloaded M4A file. 
            Defaults to user's "Downloads" folder.
    Returns:
        str: Path to the downloaded M4A file.
    """
    # Set default output path to "Downloads" default pc folder 
    if output_path is None:
        output_path = os.path.join(os.path.expanduser("~"), "Downloads")

    # Get video info dictionary if not provided, without downloading
    if info is None:
        info = get_video_info(url)
        print_video_info(info)
    
    # Create output directory if it doesn't exist
    print("Preparing to download...")
    print(f"URL: {url}")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = f"{info['track']} - {info['artist']}.m4a"
    file_path = os.path.join(output_path, file_name)
    
    # Configure yt-dlp for audio only
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Prefer M4A, fallback to best audio
        'outtmpl': file_path,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'extractor_retries': 3,
        'fragment_retries': 3,
        'sleep_interval': 3,
        'max_sleep_interval': 10,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Download the audio
            d_header = f"⬇️ ⬇️ ⬇️  Downloading: {info['title']} -"
            print(f"\n\n{d_header:-<60}")
            downloaded_file = ydl.download([url])
            print(f"✅ Download completed at {file_path}\n\n")
     
    except Exception as e:
        print(f"❌ Error downloading from {url}:"
              f"\n└─── {e}")
        return None
    print(f"{'-'*60}\n")
    return file_path

    
#%%
if __name__ == "__main__":
    """
    Script to execute and test functions defined in this module.
    """
    TEST_URL = "https://www.youtube.com/watch?v=Ez8-GezfJy4"
    print(f"Testing get_video_info with URL: {TEST_URL}")
    
    # Checking function to validade url
    test_url = get_validated_url(TEST_URL)
    
    # Checking function to get video info
    video_info = get_video_info(test_url)
    
    # Checking function to print video info
    print_video_info(video_info, select_keys=False)
    
    
    
# %%
