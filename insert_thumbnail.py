import os
from moviepy import *
from PIL import Image

def insert_thumbnail(video_path, thumbnail_path, output_path=None):
    """
    Insert a thumbnail image into the middle of a video.
    
    Args:
        video_path (str): Path to the input video file
        thumbnail_path (str): Path to the thumbnail image
        output_path (str, optional): Path to save the output video. If None, adds '_with_thumbnail' to the input filename.
    
    Returns:
        str: Path to the output video file
    """
    # Set default output path if not provided
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_with_thumbnail{ext}"
    
    # Load the video
    video = VideoFileClip(video_path)
    
    # Load the image with PIL and resize it
    img = Image.open(thumbnail_path)
    new_width = int(video.w * 0.8)
    ratio = new_width / img.width
    new_height = int(img.height * ratio)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Convert PIL Image to numpy array and create ImageClip
    import numpy as np
    thumbnail = ImageClip(np.array(img))
    
    # Set the duration of the thumbnail to 3 seconds
    thumbnail = thumbnail.with_duration(3)
    
    # Calculate the middle time of the video
    middle_time = video.duration / 2
    
    # Create a composite video with the thumbnail in the center
    final = video
    thumbnail = thumbnail.with_start(middle_time - 1.5).with_position(('center', 'center'))
    final = CompositeVideoClip([final, thumbnail])
    
    # Write the result to a file
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    return output_path

def main():
    # Define input and output paths
    input_folder = 'fix'
    video_file = os.path.join(input_folder, 'summary_video.mp4')
    thumbnail_file = os.path.join(input_folder, 'thumbnail.jpg')
    output_file = os.path.join(input_folder, 'summary_video_with_thumbnail.mp4')
    
    # Check if input files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file not found at {video_file}")
        return
    if not os.path.exists(thumbnail_file):
        print(f"Error: Thumbnail file not found at {thumbnail_file}")
        return
    
    try:
        print("Processing video...")
        output_path = insert_thumbnail(video_file, thumbnail_file, output_file)
        print(f"Success! Output saved to: {output_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
