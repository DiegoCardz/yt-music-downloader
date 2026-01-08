from mutagen.mp4 import MP4, MP4Cover
import requests
import os

#%% Function to change M4A file properties
def change_M4A_file_properties(file_path: str, metadata:dict) -> bool:
    """Change M4A file metadata properties
    
    Args:
        file_path (str): Path to the M4A file
        metadata (dict): 
            Dictionary containing metadata fields to update.
            Supported keys: track, artist, album, year, url, picture
    Returns:
        bool: True if metadata was updated successfully, False otherwise
    """
    try:
        audio = MP4(file_path)
        
        # MP4 tags mapping
        
        # Description Tags: Título, Legendas, Classificação, Marcas, Comentários
        # Título (Track name)
        if metadata.get("track"):
            print(f"Setting track name to: {metadata['track']}")
            audio["\xa9nam"] = [metadata["track"]]
        # Subtitle (Legendas)
        if metadata.get("subtitle"):
            print(f"Setting subtitle to: {metadata['subtitle']}")
            audio["\xa9sub"] = [metadata["subtitle"]]
        # Rating (Classificação)
        # Keywords (Marcas)
        # Commentary (Comentários)
        if metadata.get("commentary"):
            print(f"Setting commentary to: {metadata['commentary']}")
            audio["\xa9cmt"] = [metadata["commentary"]]
        #------------------------------------------------------------------------------
        # Artist name
        if metadata.get("artist"):
            print(f"Setting artist to: {metadata['artist']}")
            audio["\xa9ART"] = [metadata["artist"]]  # Artist
        # Participating artists
        if metadata.get("participating_artists"):
            print(f"Setting participating artists to: {metadata['participating_artists']}")
            audio["aART"] = [metadata["participating_artists"]]  # Album Artist
        
        # Origin Provider URL
        if metadata.get("url"):
            print(f"Setting origin provider URL to: {metadata['url']}")
            audio["purl"] = [metadata["url"]]  # Origin Provider URL

        # Album name
        if metadata.get("album"):
            print(f"Setting album to: {metadata['album']}")
            audio["\xa9alb"] = [metadata["album"]]  # Album
        if metadata.get("year"):
            print(f"Setting year to: {metadata['year']}")
            audio["\xa9day"] = [str(metadata["year"])]  # Year
        

        # Add album cover if provided
        if metadata.get("picture"):
            print(f"Setting album cover from: {metadata['picture']}")
            # get picture from url
            response = requests.get(metadata["picture"])
            if response.status_code == 200:
                cover_data = response.content
                audio["covr"] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
            elif isinstance(metadata["picture"], str) and os.path.exists(metadata["picture"]):
                with open(metadata["picture"], 'rb') as f:
                    cover_data = f.read()
                audio["covr"] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
            elif isinstance(metadata["picture"], bytes):
                audio["covr"] = [MP4Cover(metadata["picture"], MP4Cover.FORMAT_JPEG)]
        audio.save()
        
        print(f"✅ Metadata updated for: {os.path.basename(file_path)}")
        return True   
    except Exception as e:
        print(f"❌ Error updating metadata to file {file_path}:"
              f"\n└─── {e}")
        return False