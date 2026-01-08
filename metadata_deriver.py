import re

#%% Function to derive metadata
def derive_metadata(metadata:dict) -> dict:
    select_info_keys = {
        "id", "track", "title", "artist", "album", "year", "picture", 
        "url", 
    }
    filled_info = set(k for k in metadata.keys() if metadata[k] is not None)
    
    if select_info_keys.issubset(filled_info):
        print("✅ Essential Metadata complete!")
    else:
        try:
            metadata = derive_metadata_with_llm(metadata)
        except Exception as e:
            print(f"Error deriving metadata with LLM: {e}")
            print("Falling back to brute-force methods.")
            metadata = derive_metadata_with_brute_force(metadata)
    
    return metadata
    

#%% Function to derive missing metadata fields using brute-force methods
def derive_metadata_with_brute_force(metadata:dict) -> dict:
    """Derive missing metadata fields from existing information.
    """
    print("🦾  Deriving missing metadata fields using brute-force methods...")
    def remove_special_chars(t: str) -> str:
        """Remove special characters from a string while keeping accented letters."""
        return re.sub(r"[^\w\s\u00C0-\u024F]", "", t)
    
    # Derive artist name if missing
    def derive_artist_name(**kwargs) -> str:
        print("Deriving artist name - - - ", end="")
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
        return artist
    
    if metadata.get("artist", None) is None:
        metadata["artist"] = derive_artist_name(**metadata)
    
    
    # Derive album name if missing
    def derive_album_name(**kwargs) -> str:
        print("Deriving album name - - - ", end="")
        album = ""
        parenthesis_contents = re.findall(r"\((.*?)\)", metadata.get("title", ""))
        if parenthesis_contents:
            album = parenthesis_contents[0]
        
        # Clean up album name and set variable in dictionary
        album = remove_special_chars(album).strip().title()
        print(f"- -> {album}")
        return album
        
    if metadata.get("album", None) is None:
        metadata["album"] = derive_album_name(**metadata)

    # Derive track name if missing
    def derive_track_name(**kwargs) -> str:
        print("Deriving track name - - - ", end="")
        
        # Extract track name from title
        track = metadata.get("title", "")
        artist = metadata.get("artist", "")
        
        # Try to remove artist
        track = track.replace(artist, "").strip() 
        
        # Try to remove album
        track = track.replace(metadata.get("album",""), "").strip()
        
        # Clean up track name and set variable in dictionary
        track = remove_special_chars(track).strip().title()
        print(f"- -> {track}")
        return track
    
    if metadata.get("track", None) is None:
        metadata["track"] = derive_track_name(**metadata)
    
    # Derive year if missing
    def derive_release_year(**kwargs) -> int:
        print("Deriving release year - - - ", end="")
        year = 0
        if kwargs.get('release_year', None) is not None:
            year = kwargs['release_year']
        elif kwargs.get('upload_date', None) is not None:
            year = kwargs['upload_date'][:4]
        
        print(f"- -> {year}")
        return year
    
    if metadata.get("year", None) is None:
        metadata["year"] = derive_release_year(**metadata)

    # Derive picture if missing
    def derive_picture_url(**kwargs) -> str:
        print("Deriving picture URL - - - ", end="")
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
    
    if metadata.get("picture", None) is None:
        metadata["picture"] = derive_picture_url(**metadata)
    
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
    
    from hf_metadata_extractor import extract_metadata_from_description
    new_metadata = extract_metadata_from_description(description)
    
    # Update derived fields
    for key, value in new_metadata.items():
        key_map = {
            "Artist": "artist",
            "Participating Artists": "participating_artists",
            "Album": "album",
            "Original song": "commentary",
            "Composers": "composer",
            "Release Year": "year",
            "Genre": "genre",
        }
        mapped_key = key_map.get(key, None)
        if mapped_key:
            metadata[mapped_key] = value
            
    return metadata

# %%
