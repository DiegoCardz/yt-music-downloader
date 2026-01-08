#%% Imports
from downloader import (
    get_validated_url,
    download_M4A_audio,
    get_video_info,
)
from updater import change_M4A_file_properties



#%% Main execution
urls = []
print("Enter YouTube URLs or press 'ENTER' to continue:")
counter = 0
while True:
    counter += 1
    user_input = input(f'URL #{counter}: ').strip()
    if user_input == "":
        break
    urls.append(user_input)

bad_urls = []
for url in urls:
    try:
        validated_url = get_validated_url(url)
        info = get_video_info(validated_url)
        file_path = download_M4A_audio(validated_url, info)
        try:
            change_M4A_file_properties(file_path, info)
        except Exception as e:
            print(f"Error changing file properties for {file_path}: {e}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        bad_urls.append(url)
    print("\n"+"="*60)

print("All done!")
if bad_urls:
    print("The following URLs could not be processed:")
    for bad_url in bad_urls:
        print(f"- {bad_url}")

# %%
