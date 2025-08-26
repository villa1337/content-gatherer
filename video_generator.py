import os
from moviepy import *
from PIL import Image

def resize_and_pad(img, target_size=(1080, 1920), background_color=(0, 0, 0)):
    """
    Resize the image to fit within target_size (preserving aspect ratio),
    and pad it with background_color to make it exactly target_size.
    """
    img_ratio = img.width / img.height
    target_ratio = target_size[0] / target_size[1]

    # Resize while keeping aspect ratio
    if img_ratio > target_ratio:
        # Image is wider
        new_width = target_size[0]
        new_height = round(new_width / img_ratio)
    else:
        # Image is taller (or same ratio)
        new_height = target_size[1]
        new_width = round(new_height * img_ratio)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    # Create background canvas
    background = Image.new("RGB", target_size, background_color)
    paste_x = (target_size[0] - new_width) // 2
    paste_y = (target_size[1] - new_height) // 2

    background.paste(resized_img, (paste_x, paste_y))
    return background

def create_slideshow(folder_path):
    audio_path = os.path.join(folder_path, "summary_audio.mp3")
    output_video_path = os.path.join(folder_path, "summary_video.mp4")

    # Ask if user wants to use a custom thumbnail
    use_custom_thumbnail = input("\nDo you want to use a custom thumbnail? (y/n): ").strip().lower() == 'y'
    custom_thumbnail_path = os.path.join(folder_path, "thumbnail.jpg")
    
    if use_custom_thumbnail and not os.path.exists(custom_thumbnail_path):
        print(f"⚠️  Custom thumbnail not found at {custom_thumbnail_path}. Proceeding without it.")
        use_custom_thumbnail = False

    # Load audio and get duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # Load image files (sorted)
    image_files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])

    if not image_files:
        raise Exception("❌ No images found in the folder.")

    image_clips = []
    valid_images = []

    for i, img_path in enumerate(image_files):
        try:
            img = Image.open(img_path).convert("RGB")
            padded_img = resize_and_pad(img)

            # Save padded version temporarily
            padded_path = os.path.join(folder_path, f"_padded_{i}.jpg")
            padded_img.save(padded_path)
            valid_images.append(padded_path)
            
            print(f"✅ Processed image: {img_path}")
            
        except Exception as e:
            print(f"⚠️  Skipping invalid image {img_path}: {e}")
            continue
    
    if not valid_images:
        raise Exception("❌ No valid images found after processing.")

    # Insert custom thumbnail in the middle if requested
    if use_custom_thumbnail:
        try:
            # Process the custom thumbnail
            img = Image.open(custom_thumbnail_path).convert("RGB")
            padded_img = resize_and_pad(img)
            padded_path = os.path.join(folder_path, "_padded_thumbnail.jpg")
            padded_img.save(padded_path)
            
            # Insert in the middle of the slideshow
            middle_index = len(valid_images) // 2
            valid_images.insert(middle_index, padded_path)
            print(f"✅ Added custom thumbnail at position {middle_index}")
            
            # No need to adjust duration here as we'll calculate per_image_duration after this
            
        except Exception as e:
            print(f"⚠️  Failed to process custom thumbnail: {e}")
    # If no custom thumbnail, move first image to middle for better thumbnail selection
    elif len(valid_images) > 2:
        first_img = valid_images.pop(0)
        middle_index = len(valid_images) // 2
        valid_images.insert(middle_index, first_img)
    
    # Calculate duration per image based on reordered valid images
    num_images = len(valid_images)
    middle_index = num_images // 2
    
    # Calculate duration for regular images (slightly less than even split)
    regular_duration = (duration * 0.8) / (num_images + 0.5)  # Reserve 20% extra for middle image
    middle_duration = duration - (regular_duration * (num_images - 1))  # Remaining time for middle image
    
    for i, padded_path in enumerate(valid_images):
        # Use longer duration for middle image
        clip_duration = middle_duration if i == middle_index else regular_duration
        clip = ImageClip(padded_path).with_duration(clip_duration)
        image_clips.append(clip)
        print(f"Image {i+1}/{num_images} duration: {clip_duration:.2f}s" + (" (middle, extended)" if i == middle_index else ""))
    
    # Concatenate video
    slideshow = concatenate_videoclips(image_clips, method="compose")
    slideshow = slideshow.with_audio(audio_clip)

    # Export video
    slideshow.write_videofile(
        output_video_path,
        fps=24,
        codec="libx264",           # Windows-compatible codec
        audio_codec="aac",
        preset="veryfast",
        ffmpeg_params=[
            "-pix_fmt", "yuv420p",  # required for wide compatibility
            "-b:v", "3M"            # target video bitrate (adjust)
        ]
    )

    print(f"✅ Slideshow created: {output_video_path}")

    # Cleanup temp padded images
    for padded in valid_images:
        try:
            if padded.startswith(os.path.join(folder_path, "_padded_")):
                os.remove(padded)
        except:
            pass