import whisper
import sounddevice as sd
import numpy as np
import queue
import wave
import pyttsx3
import tempfile
import time
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Load Whisper model
model = whisper.load_model("base")

# Initialize Groq (LLaMA3) for smart replies
groq_chat = ChatGroq(model_name="llama3-70b-8192", api_key=groq_api_key)

# Queue for audio data
q = queue.Queue()

# Voice output engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # Adjust speaking speed

# System prompt for assistant behavior
conversation = [
    {"role": "system", "content": "You are a helpful and friendly AI assistant that speaks to the user based on their voice input. Be concise and conversational."}
]

def record_callback(indata, frames, time_info, status):
    q.put(indata.copy())

def save_wav(audio, filename="temp.wav", samplerate=16000):
    with wave.open(filename, mode='wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(samplerate)
        wf.writeframes(audio.astype(np.int16).tobytes())
    return filename

def listen_and_transcribe():
    duration = 5  # seconds
    samplerate = 16000

    print("🎤 Listening...")

    with sd.InputStream(callback=record_callback, channels=1, samplerate=samplerate, dtype='int16'):
        audio_data = []
        start_time = time.time()
        while time.time() - start_time < duration:
            audio_data.append(q.get())
        audio = np.concatenate(audio_data, axis=0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        wav_path = save_wav(audio, tmp.name)

    result = model.transcribe(wav_path)
    os.remove(wav_path)
    return result["text"]

def speak(text):
    print(f"🤖 Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def ask_groq(text):
    conversation.append({"role": "user", "content": text})
    response = groq_chat.invoke(conversation)
    reply = response.content
    conversation.append({"role": "assistant", "content": reply})
    return reply

# 🔁 Main loop
if __name__ == "__main__":
    print("🟢 Voice Assistant is running. Speak into your mic...")

    while True:
        try:
            user_text = listen_and_transcribe()
            print(f"🧍 You: {user_text}")
            if user_text.strip() == "":
                continue
            ai_reply = ask_groq(user_text)
            speak(ai_reply)
        except KeyboardInterrupt:
            print("\n🛑 Assistant stopped.")
            break
        except Exception as e:
            print("❌ Error:", e)
