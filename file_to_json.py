import json
import os
import re
from datetime import datetime
import groq_query
import image_fetch

def sanitize_filename_from_title(title):
    """Generate a safe filename from a title."""
    filename = title.lower()
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip('_')
    if len(filename) > 50:
        filename = filename[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{filename}_{timestamp}"

def create_json_from_file(input_file_path="input/input.txt", output_folder="output"):
    """
    Extract information from a text file and save it as a JSON file.
    
    Args:
        input_file_path (str): Path to the input text file
        output_folder (str): The folder to save JSON files (default: "output")
    
    Returns:
        tuple: (article_folder, summary)
    """
    try:
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
        
        with open(input_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        lines = content.split('\n')
        title = lines[0].strip()
        summary_start = 1
        while summary_start < len(lines) and lines[summary_start].strip() == '':
            summary_start += 1
        full_text = '\n'.join(lines[summary_start:]).strip()

        if not title or not full_text:
            raise ValueError("File must contain a title on the first line and content after line breaks")
        
        print(f"Processing file: {input_file_path}")
        print(f"Title: {title}")
        print(f"Content length: {len(full_text)} characters")

        if len(full_text) <= 750:
            print("📝 Using original text as summary (short content)")
            final_summary = full_text
        else:
            print("📝 Generating summary...")
            final_summary = groq_query.get_summary({"text": full_text})

        content_dict = {
            "title": title,
            "text": full_text,
            "authors": ["File Input"],
            "publish_date": None
        }

        print("Extracting keywords...")
        key_words = groq_query.get_key_words(content_dict)

        print("Generating YouTube title...")
        youtube_title = groq_query.get_youtube_title(content_dict)

        print("Generating YouTube description...")
        youtube_description = groq_query.get_youtube_description(content_dict)

        filename = sanitize_filename_from_title(title)
        article_folder = os.path.join(output_folder, filename)
        os.makedirs(article_folder, exist_ok=True)

        print("Fetching and downloading related images...")
        image_urls, image_paths = image_fetch.fetch_and_download_images(key_words, article_folder)

        data = {
            "source": "file_input",
            "input_file": input_file_path,
            "title": title,
            "summary": final_summary,
            "keywords": key_words,
            "youtube_title": youtube_title,
            "youtube_description": youtube_description,
            "image_urls": image_urls,
            "image_paths": image_paths,
            "authors": ["File Input"],
            "publish_date": None,
            "extracted_at": datetime.now().isoformat(),
            "text_preview": final_summary[:500] + "..." if len(final_summary) > 500 else final_summary
        }

        json_path = os.path.join(article_folder, f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ JSON file saved: {json_path}")
        return article_folder, final_summary

    except Exception as e:
        print(f"❌ Error processing file {input_file_path}: {str(e)}")
        raise
