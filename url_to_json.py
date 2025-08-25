import json
import os
from datetime import datetime
from urllib.parse import urlparse
import re
import groq_query
import news_extract
import image_fetch

def create_json_from_url(url, output_folder="output"):
    """
    Extract information from a URL and save it as a JSON file.
    
    Args:
        url (str): The URL to process
        output_folder (str): The folder to save JSON files (default: "json_outputs")
    
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
        
        # Fetch related image URLs
        print("Fetching related image URLs...")
        image_urls = image_fetch.fetch_urls(key_words)

        # Create the data structure
        data = {
            "url": url,
            "title": content["title"],
            "summary": summary,
            "keywords": key_words,
            "youtube_title": youtube_title,
            "youtube_description": youtube_description,
            "image_urls": image_urls,
            "authors": content["authors"],
            "publish_date": str(content["publish_date"]) if content["publish_date"] else None,
            "extracted_at": datetime.now().isoformat(),
            "text_preview": content["text"][:500] + "..." if len(content["text"]) > 500 else content["text"]
        }
        
        # Generate filename from URL
        filename = generate_filename_from_url(url)
        
        # Create nested folder structure: output/<folder_name>/<json_file>
        folder_path = os.path.join(output_folder, filename)
        os.makedirs(folder_path, exist_ok=True)
        
        filepath = os.path.join(folder_path, f"{filename}.json")
        
        # Download images
        image_fetch.download_images(image_urls, folder_path)
        
        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON file saved: {filepath}")
        return folder_path, summary
        
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
            result = create_json_from_url(url, output_folder)
            results.append({"url": url, "status": "success", "data": result})
        except Exception as e:
            print(f"Failed to process {url}: {str(e)}")
            results.append({"url": url, "status": "error", "error": str(e)})
    
    return results