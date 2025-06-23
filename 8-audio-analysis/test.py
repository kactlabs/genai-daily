"""
Simple test script for AssemblyAI audio transcription
"""

import os
from dotenv import load_dotenv
import assemblyai as aai

# Load environment variables
load_dotenv()

# Configure AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def test_transcription():
    """Test basic transcription functionality"""
    
    # Test with a sample audio URL
    audio_url = "https://assembly.ai/wildfires.mp3"
    
    print("🎵 Testing AssemblyAI transcription...")
    print(f"Audio URL: {audio_url}")
    
    # Configure transcription
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        sentiment_analysis=True,
        summarization=True,
        iab_categories=True
    )
    
    # Create transcriber and process audio
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_url, config=config)
    
    # Check status
    if transcript.status == aai.TranscriptStatus.error:
        print(f"❌ Transcription failed: {transcript.error}")
        return False
    
    print("✅ Transcription completed successfully!")
    
    # Display results
    print("\n📝 TRANSCRIPT:")
    print("-" * 50)
    print(transcript.text[:500] + "..." if len(transcript.text) > 500 else transcript.text)
    
    if hasattr(transcript, 'summary') and transcript.summary:
        print("\n📋 SUMMARY:")
        print("-" * 50)
        print(transcript.summary)
    
    if hasattr(transcript, 'utterances') and transcript.utterances:
        print(f"\n👥 SPEAKERS: {len(set(str(u.speaker) for u in transcript.utterances))} detected")
    
    if hasattr(transcript, 'sentiment_analysis') and transcript.sentiment_analysis:
        sentiments = [str(s.sentiment) for s in transcript.sentiment_analysis]
        print(f"😊 SENTIMENT: {len(sentiments)} segments analyzed")
    
    if hasattr(transcript, 'iab_categories') and transcript.iab_categories:
        topics = transcript.iab_categories.summary
        if topics:
            top_topic = max(topics.items(), key=lambda x: x[1])
            print(f"🏷️ TOP TOPIC: {top_topic[0]} ({top_topic[1]*100:.1f}%)")
    
    return True

if __name__ == "__main__":
    # Check if API key is configured
    if not os.getenv("ASSEMBLYAI_API_KEY"):
        print("❌ ASSEMBLYAI_API_KEY not found in environment variables")
        print("Please check your .env file")
        exit(1)
    
    # Run test
    success = test_transcription()
    
    if success:
        print("\n🎉 All tests passed! The audio analysis toolkit is ready to use.")
    else:
        print("\n❌ Tests failed. Please check your configuration.")
