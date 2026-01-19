import re

#%% Function to derive metadata
def derive_metadata(metadata:dict) -> dict:
    metadata["picture"] = get_picture_url(**metadata)
    metadata["subtitles_url"] = get_subtitles_url(**metadata)
    
    select_info_keys = {
        "id", "track", "title", "artist", "album", "year", "picture", 
        "url", "lyrics"
    }
    filled_info = set(k for k in metadata.keys() if metadata[k] is not None)
    
    if select_info_keys.issubset(filled_info):
        print("✅ Essential Metadata complete!")
    else:
        metadata = derive_metadata_with_llm(metadata)
        filled_info = set(k for k in metadata.keys() if metadata[k] is not None)
    
    if select_info_keys.issubset(filled_info):
        print("✅ Essential Metadata complete!")
    else:
        print("Falling back to brute-force methods.")
        metadata = derive_metadata_with_brute_force(metadata)
    
    return metadata
    
# %% ================================================================================== 
# Functions to get metadata fields that are not loaded by default with yt-dlp
# =====================================================================================

# Get picture
def get_picture_url(**kwargs) -> str:
    print("🛸 Extracting picture URL - - - ", end="")
    picture_url = ""
    # Try to use thumbnail URL as picture
    if kwargs.get("thumbnail", None) is not None:
        picture_url = kwargs["thumbnail"]
    
    elif kwargs.get("thumbnails", None) is not None:
        thumbnails = kwargs["thumbnails"]
        if isinstance(thumbnails, list) and len(thumbnails) > 0:
            # Use the highest resolution thumbnail
            picture_url = thumbnails[-1].get("url", "")
    
    print(f"- -> {picture_url}")
    return picture_url


# Get URL to subtitles data
def get_subtitles_url(**kwargs) -> str:
    print("🛸 Extracting subtitles URL - - - ", end="")
    sub_url = None
    language = kwargs.get("language")  # Original video language
    
    # Try each source in order
    for source_key in ["requested_subtitles", "automatic_captions"]:
        source = kwargs.get(source_key, {})
        if not source:
            continue
        
        langs_to_try = [language] if language else []
        langs_to_try.extend(["pt-BR", "pt", "en"])
        
        # Try each language in order
        for lang in langs_to_try:
            if lang in source:
                sub_url = source[lang].get("url", None)
                if sub_url:
                    print(f"- -> Found (from {source_key} - {lang} subtitles)")
                    return sub_url
     
    print(f"- -> Not available")
    return sub_url
    
    
# %% ================================================================================== 
# Functions to derive missing metadata fields using brute-force methods
# =====================================================================================

# Remove special characters from a string while keeping accented letters.
def remove_special_chars(t: str) -> str:
    """Remove special characters from a string while keeping accented letters."""
    return re.sub(r"[^\w\s\u00C0-\u024F]", "", t)


# Derive artist name with brute-force
def derive_artist_name(**kwargs) -> str:
    print("🦾 Deriving artist name - - - ", end="")
    artist = ""
    # Try to use uploader name as artist
    if kwargs.get("uploader", None) is not None:
        artist = kwargs["uploader"]
    else:
        # Try to split title by common separators
        title = kwargs.get("title", "")
        possible_separators = [" - ", " | ", " — ", " ~ "]
        for sep in possible_separators:
            if sep in title:
                artist = title.split(sep)[1].strip()
    
    print("Derived artist name:", artist)
    artist = remove_special_chars(artist).strip().title()
    if not artist:
        artist = "Artist"
    return artist


# Derive album name if missing
def derive_album_name(**kwarg) -> str:
    print("🦾 Deriving album name - - - ", end="")
    album = ""
    parenthesis_contents = re.findall(r"\((.*?)\)", kwarg.get("title", ""))
    if parenthesis_contents:
        album = parenthesis_contents[0]
    
    # Clean up album name and set variable in dictionary
    album = remove_special_chars(album).strip().title()
    print(f"- -> {album}")
    return album
    

# Derive track name with brute-force
def derive_track_name(**kwarg) -> str:
    print("🦾 Deriving track name - - - ", end="")
    
    # Extract track name from title
    track = kwarg.get("title", "")
    artist = kwarg.get("artist", "")
    
    # Try to remove artist
    track = track.replace(artist, "").strip() 
    
    # Try to remove album
    track = track.replace(kwarg.get("album",""), "").strip()
    
    # Clean up track name and set variable in dictionary
    track = remove_special_chars(track).strip().title()
    
    if not track:
        track = "Track"
    
    print(f"- -> {track}")
    return track


# Derive year if missing
def derive_release_year(**kwargs) -> int:
    print("🦾 Deriving release year - - - ", end="")
    year = 0
    if kwargs.get('release_year', None) is not None:
        year = kwargs['release_year']
    elif kwargs.get('upload_date', None) is not None:
        year = kwargs['upload_date'][:4]
    
    print(f"- -> {year}")
    return year


# %% ================================================================================== 
# Functions to actually derive missing metadata fields by calling the above ones
# =====================================================================================
def derive_metadata_with_brute_force(metadata:dict) -> dict:
    """Derive missing metadata fields from existing information.
    """
    print("🦾  Deriving missing metadata fields using brute-force methods...")
    
    if metadata.get("artist", None) is None:
        metadata["artist"] = derive_artist_name(**metadata)
    
    if metadata.get("album", None) is None:
        metadata["album"] = derive_album_name(**metadata)
    
    if metadata.get("track", None) is None:
        metadata["track"] = derive_track_name(**metadata)
    
    if metadata.get("year", None) is None:
        metadata["year"] = derive_release_year(**metadata)
    
    if metadata.get("picture", None) is None:
        metadata["picture"] = get_picture_url(**metadata)
    
    return metadata

#%% Function to derive missing metadata fields using a language model
def derive_metadata_with_llm(metadata:dict) -> dict:
    """Derive missing metadata fields using a language model.
    """
    description = metadata.get("description", None)
    if not description:
        print("No description available for LLM-based metadata derivation.")
        return metadata  # Not enough info to derive metadata
    
    print("🤖  Deriving missing metadata fields using LLM..."  )
    
    from hf_metadata_extractor import (
        extract_metadata_from_description, 
        print_extracted_metadata,
    )
    new_metadata = extract_metadata_from_description(description)
    print_extracted_metadata(new_metadata)
    
    print(f"📠 Updating metadata with derived fields: {new_metadata.keys()}")
    # Update derived fields
    for key, value in new_metadata.items():
        key_map = {
            'Track': "track",
            "Artist": "artist",
            "Participating Artists": "participating_artists",
            "Album": "album",
            "Original song": "original_song",
            "Composers": "composer",
            "Release Year": "year",
            "Genre": "genre",
            "Lyrics": "lyrics",
        }
        
        mapped_key = key_map.get(key, None)
        if mapped_key:
            metadata[mapped_key] = value
            
    return metadata

# %%
