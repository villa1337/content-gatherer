import requests
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables once at module level
load_dotenv()
UNSPLASH_API_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

def fetch_and_download_images(words, output_folder, max_results=1):
    """
    Search for and download images from Unsplash for given keywords.
    
    Args:
        words (list): List of keywords to search for
        output_folder (str): Path to save the downloaded images
        max_results (int): Maximum number of images per keyword
        
    Returns:
        tuple: (list of image URLs, list of downloaded file paths)
    """
    if not words:
        print("⚠️ No keywords provided for image search")
        return [], []
        
    if not UNSPLASH_API_KEY:
        print("⚠️ No Unsplash API key found")
        return [], []
    
    os.makedirs(output_folder, exist_ok=True)
    headers = {
        'Authorization': f'Client-ID {UNSPLASH_API_KEY}',
        'Accept-Version': 'v1'
    }
    
    all_urls = []
    downloaded_paths = []
    img_count = 0
    
    print(f"🔍 Processing keywords: {', '.join(words)}")
    
    for word in words:
        try:
            print(f"\nℹ️ Searching for '{word}'...")
            
            # Search Unsplash
            url = f'https://api.unsplash.com/search/photos?query={quote_plus(word)}&per_page={max_results}'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Get image URLs from results
            results = response.json().get('results', [])
            if not results:
                print(f"⚠️ No images found for '{word}'")
                continue
                
            # Process each result
            for result in results:
                image_url = result.get('urls', {}).get('regular')
                if not image_url:
                    continue
                    
                try:
                    # Download the image
                    print(f"📥 Downloading image for '{word}'...")
                    img_response = requests.get(image_url, timeout=10)
                    img_response.raise_for_status()
                    
                    # Save the image
                    filename = f"img{img_count}.jpg"
                    file_path = os.path.join(output_folder, filename)
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"✅ Saved: {file_path}")
                    all_urls.append(image_url)
                    downloaded_paths.append(file_path)
                    img_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to download image for '{word}': {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error processing '{word}': {str(e)}")
            continue
    
    print(f"\n📊 Successfully downloaded {len(downloaded_paths)} images")
    return all_urls, downloaded_paths