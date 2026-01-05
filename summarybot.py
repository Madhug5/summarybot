import re
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# Configure OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # Replace with your OpenRouter API key
)

def extract_video_id(youtube_url):
    """Extract video ID from YouTube URL"""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")

def get_transcript(video_id):
    """Fetch transcript for a YouTube video"""
    try:
        # Create an instance of YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        
        # Use the instance to get transcript list
        transcript_list = api.list(video_id)
        
        # Try to find English transcript
        transcript = transcript_list.find_transcript(['en'])
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Combine all text - access as attributes
        full_text = " ".join(snippet.text for snippet in transcript_data)
        print(f"✅ Transcript fetched: {len(full_text)} characters")
        return full_text
        
    except Exception as e:
        raise Exception(f"Could not fetch transcript: {e}")

def summarize_transcript(transcript):
    """Summarize transcript using OpenRouter"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",  # You can change this to other models
            messages=[
                {"role": "system", "content": "You summarize YouTube lectures clearly."},
                {"role": "user", "content": f"""
Summarize the following lecture:
- 5 bullet points
- simple language
- key ideas only

Transcript:
{transcript}
"""}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenRouter API error: {e}")

def summarize_youtube_video(youtube_url):
    """Main function to summarize a YouTube video"""
    video_id = extract_video_id(youtube_url)
    print(f"📹 Video ID: {video_id}")
    print("🔄 Fetching transcript...")
    transcript = get_transcript(video_id)
    print("🤖 Generating summary...")
    return summarize_transcript(transcript)

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video link: ")
    print()
    try:
        summary = summarize_youtube_video(youtube_url)
        print("\n📌 Lecture Summary:\n")
        print(summary)
    except Exception as e:
        print(f"\n❌ Error: {e}")