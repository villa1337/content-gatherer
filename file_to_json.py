import json
import os
from datetime import datetime
import groq_query
import image_fetch

def create_json_from_file(input_file_path="input/input.txt", output_folder="output"):
    """
    Extract information from a text file and save it as a JSON file.
    
    Args:
        input_file_path (str): Path to the input text file
        output_folder (str): The folder to save JSON files (default: "output")
    
    Returns:
        tuple: (folder_path, summary) - The folder path and summary text
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
        
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Parse the file content (first line = title, rest = summary after line breaks)
        lines = content.split('\n')
        title = lines[0].strip()
        
        # Find where the summary starts (after empty lines)
        summary_start = 1
        while summary_start < len(lines) and lines[summary_start].strip() == '':
            summary_start += 1
        
        summary = '\n'.join(lines[summary_start:]).strip()
        
        if not title or not summary:
            raise ValueError("File must contain a title on the first line and summary after line breaks")
        
        print(f"Processing file content...")
        print(f"Title: {title}")
        print(f"Summary length: {len(summary)} characters")
        
        # Determine if content is short enough to skip summary generation
        # Use character count as threshold
        char_count = len(summary)
        
        # If content is short (like your example: ~400 chars), skip summary
        if char_count <= 750:
            print(f"📝 Content is short ({char_count} chars) - using original text as summary")
            final_summary = summary
        else:
            print(f"📝 Content is long ({char_count} chars) - generating summary...")
            final_summary = groq_query.get_summary({"text": summary})
        
        # Create content structure similar to news_extract format
        file_content = {
            "title": title,
            "text": summary,  # Keep original for keyword generation
            "authors": ["File Input"],
            "publish_date": None
        }
        
        # Get keywords for image search
        print("Extracting keywords...")
        key_words = groq_query.get_key_words(file_content)
        
        # Generate YouTube optimization content
        print("Generating YouTube title...")
        youtube_title = groq_query.get_youtube_title(file_content)
        
        print("Generating YouTube description...")
        youtube_description = groq_query.get_youtube_description(file_content)
        
        # Fetch image URLs based on keywords
        print("Fetching related image URLs...")
        image_urls = image_fetch.fetch_urls(key_words)
        
        # Create the data structure
        data = {
            "source": "file_input",
            "input_file": input_file_path,
            "title": title,
            "summary": final_summary,  # Use the processed summary (original or generated)
            "keywords": key_words,
            "youtube_title": youtube_title,
            "youtube_description": youtube_description,
            "image_urls": image_urls,
            "authors": ["File Input"],
            "publish_date": None,
            "extracted_at": datetime.now().isoformat(),
            "text_preview": final_summary[:500] + "..." if len(final_summary) > 500 else final_summary
        }
        
        # Generate filename from title
        filename = generate_filename_from_title(title)
        
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
        return folder_path, final_summary
        
    except Exception as e:
        print(f"❌ Error processing file {input_file_path}: {str(e)}")
        raise

def generate_filename_from_title(title):
    """
    Generate a safe filename from a title.
    
    Args:
        title (str): The title to convert
        
    Returns:
        str: A safe filename
    """
    import re
    from datetime import datetime
    
    # Clean up the title and create filename
    filename_base = title.lower()
    
    # Replace spaces and invalid characters with underscores
    filename = re.sub(r'[^\w\-_.]', '_', filename_base)
    
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    # Limit length
    if len(filename) > 50:
        filename = filename[:50]
    
    # Add timestamp to ensure uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{filename}_{timestamp}"
