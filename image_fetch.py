from ddgs import DDGS
import requests
import os
from PIL import Image
from io import BytesIO

def fetch_images(query, max_results=5):
    """
    Fetch image URLs using DuckDuckGo image search.
    """
    try:
        with DDGS() as ddgs:
            print(f"🔍 Searching for images with query: '{query}'")
            results = list(ddgs.images(query, max_results=max_results))
            
            if not results:
                print("⚠️  No results found for query:", query)
                return []
                
            print(f"ℹ️  Found {len(results)} results for query: {query}")
            
            # Debug: Print first result structure if available
            if results:
                print("ℹ️  First result structure:", {k: type(v) for k, v in results[0].items()})
                print("ℹ️  First result keys:", results[0].keys())
            
            # Try different possible keys for image URL
            image_urls = []
            for r in results[:max_results]:
                url = r.get("image") or r.get("url") or r.get("thumbnail")
                if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                    image_urls.append(url)
            
            return image_urls
            
    except Exception as e:
        print(f"❌ Error in fetch_images for query '{query}': {str(e)}")
        return []

def download_images(image_urls, save_dir="images"):
    """
    Download image URLs to a local directory.
    """
    os.makedirs(save_dir, exist_ok=True)
    successful_downloads = 0
    
    for idx, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Check if the response content type is an image
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                print(f"⚠️  Skipping {url}: Not an image (content-type: {content_type})")
                continue
            
            # Validate that the content is actually a valid image
            try:
                # Try to open the image with PIL to validate it
                img = Image.open(BytesIO(response.content))
                img.verify()  # Verify it's a valid image
                
                # Re-open for size checking (verify() closes the image)
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                
                # Filter out very small images (likely thumbnails or icons)
                if width < 300 or height < 300:
                    print(f"⚠️  Skipping {url}: Image too small ({width}x{height})")
                    continue
                
                # Filter out very wide/narrow images (likely banners or weird crops)
                aspect_ratio = width / height
                if aspect_ratio > 3 or aspect_ratio < 0.3:
                    print(f"⚠️  Skipping {url}: Bad aspect ratio ({width}x{height})")
                    continue
                
                # If validation passes, save the file
                file_path = os.path.join(save_dir, f"img{idx}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {file_path} ({width}x{height})")
                successful_downloads += 1
                
            except Exception as img_error:
                print(f"⚠️  Skipping {url}: Invalid image data ({img_error})")
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {url}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error downloading {url}: {e}")
    
    print(f"📊 Successfully downloaded {successful_downloads}/{len(image_urls)} images")

def fetch_and_download_images(words):
    image_urls = fetch_urls(words)
    download_images(image_urls)
    return image_urls

import time

def fetch_urls(words):
    """
    Fetch image URLs for a list of keywords.
    
    Args:
        words (list): List of keywords to search for images
        
    Returns:
        list: List of image URLs
    """
    if not words:
        print("⚠️  No keywords provided for image search")
        return []
        
    print(f"🔍 Fetching images for keywords: {', '.join(words)}")
    image_urls = []
    
    for word in words:
        try:
            print(f"\nℹ️  Searching for keyword: {word}")
            urls = fetch_images(word, max_results=1)
            if urls:
                print(f"✅ Found {len(urls)} images for '{word}': {urls[0]}")
                image_urls.extend(urls)
            else:
                print(f"⚠️  No images found for keyword: {word}")
            
            # Add delay between searches to avoid rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error fetching images for keyword '{word}': {str(e)}")
    
    print(f"\n📊 Found {len(image_urls)} total images for {len(words)} keywords")
    return image_urls