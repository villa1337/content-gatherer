import requests

def tts_elevenlabs(text, output_path, api_key, voice_id="JBFqnCBsd6RMkjVDRZzb"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "audio" not in content_type:
            print("❌ Response is not audio. Here's the message:")
            print(response.text)
            return  # Don't write invalid content to output file

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Audio saved successfully to {output_path}")

    except requests.exceptions.HTTPError as e:
        print(f"🚨 HTTP Error: {e}")
        print(f"Response content: {response.text}")
        raise
    except Exception as e:
        print(f"🚨 Error generating TTS: {e}")
        raise