import json
import os
from datetime import datetime
from urllib.parse import urlparse
import re
import groq_query
import news_extract
import image_fetch

def sanitize_filename(url):
    """Convert a URL into a safe filename."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Clean up the path
    if path:
        path_parts = path.split('/')
        name = path_parts[-1] if path_parts[-1] else path_parts[-2]
    else:
        name = domain
    
    # Remove file extensions
    name = re.sub(r'\.(html|htm|php|asp|aspx)$', '', name)
    
    # Replace invalid characters
    return re.sub(r'[^\w\-_.]', '_', name)

def create_json_from_url(url, output_folder="output"):
    """
    Extract information from a URL and save it as a JSON file.
    
    Args:
        url (str): The URL to process
        output_folder (str): The folder to save JSON files (default: "output")
    
    Returns:
        dict: The extracted data that was saved to JSON
    """
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Extract article content
        print(f"Extracting content from: {url}")
        content = news_extract.extract_article(url)
        
        # Get summary and keywords using Groq
        print("Generating summary...")
        summary = groq_query.get_summary(content)
        
        print("Extracting keywords...")
        key_words = groq_query.get_key_words(content)
        
        # Generate YouTube optimization content
        print("Generating YouTube title...")
        youtube_title = groq_query.get_youtube_title(content)
        
        print("Generating YouTube description...")
        youtube_description = groq_query.get_youtube_description(content)
        
        # Generate filename for the article
        filename = sanitize_filename(url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        article_name = f"{filename}_{timestamp}"
        
        # Create folder for this article's files
        article_folder = os.path.join(output_folder, article_name)
        os.makedirs(article_folder, exist_ok=True)
        
        # Fetch related image URLs and download images
        print("Fetching and downloading related images...")
        image_urls, image_paths = image_fetch.fetch_and_download_images(key_words, article_folder)

        # Create the data structure
        data = {
            "url": url,
            "title": content["title"],
            "summary": summary,
            "keywords": key_words,
            "youtube_title": youtube_title,
            "youtube_description": youtube_description,
            "image_urls": image_urls,
            "image_paths": image_paths,  # Add downloaded image paths
            "authors": content["authors"],
            "publish_date": str(content["publish_date"]) if content["publish_date"] else None,
            "extracted_at": datetime.now().isoformat(),
            "text_preview": content["text"][:500] + "..." if len(content["text"]) > 500 else content["text"]
        }
        
        # Save JSON file in the article folder
        filepath = os.path.join(article_folder, f"{article_name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON file saved: {filepath}")
        return article_folder, summary
        
    except Exception as e:
        print(f"❌ Error processing URL {url}: {str(e)}")
        raise

def generate_filename_from_url(url):
    """
    Generate a safe filename from a URL.
    
    Args:
        url (str): The URL to convert
        
    Returns:
        str: A safe filename
    """
    # Parse the URL
    parsed = urlparse(url)
    
    # Create base filename from domain and path
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Clean up the path and create filename
    if path:
        # Take the last part of the path (usually the article slug)
        path_parts = path.split('/')
        filename_base = path_parts[-1] if path_parts[-1] else path_parts[-2]
    else:
        filename_base = domain
    
    # Remove file extensions and clean up
    filename_base = re.sub(r'\.(html|htm|php|asp|aspx)$', '', filename_base)
    
    # Replace invalid characters with underscores
    filename = re.sub(r'[^\w\-_.]', '_', filename_base)
    
    # Add timestamp to ensure uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{filename}_{timestamp}"

def batch_process_urls(urls, output_folder="output"):
    """
    Process multiple URLs and save each as a JSON file.
    
    Args:
        urls (list): List of URLs to process
        output_folder (str): The folder to save JSON files
        
    Returns:
        list: List of results for each URL
    """
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n--- Processing URL {i}/{len(urls)} ---")
        try:
            article_folder, summary = create_json_from_url(url, output_folder)
            results.append({
                "url": url,
                "status": "success",
                "folder": article_folder,
                "summary": summary
            })
            print(f"📁 Output folder: {article_folder}")
            print(f"📝 Summary: {summary}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Failed to process {url}: {error_msg}")
            results.append({
                "url": url,
                "status": "error",
                "error": error_msg
            })
    
    return results
    return results