import url_to_json
import file_to_json
import text_to_speech
import os
import video_generator

def main():
    print("🎬 Content Gatherer - Video Generator")
    print("Choose your input method:")
    print("1. URL (extract from web article)")
    print("2. File (read from input/input.txt)")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            # URL input (existing workflow)
            url = input("Enter URL: ")
            folder_path, summary = url_to_json.create_json_from_url(url)
            break
        elif choice == "2":
            # File input (new workflow)
            input_file = "input/input.txt"
            if not os.path.exists(input_file):
                print(f"❌ Input file not found: {input_file}")
                print("Please create the file with:")
                print("- First line: Your story title")
                print("- Empty lines")
                print("- Rest: Your story summary/content")
                continue
            
            folder_path, summary = file_to_json.create_json_from_file(input_file)
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")
    
    # Generate audio and video (same for both workflows)
    audio_path = os.path.join(folder_path, "summary_audio.mp3")
    text_to_speech.tts_elevenlabs(summary, audio_path, "sk_85fee4f798f30152c13019e802dc41aa9b38407bdb6d32ac")
    video_generator.create_slideshow(folder_path)
    
    print(f"\n🎉 Content generation complete!")
    print(f"📁 Output folder: {folder_path}")

if __name__ == "__main__":
    main()
