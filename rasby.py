# Google Gemini-Powered Voice Assistant
# By Raifons/Bruno
# Tested and working on Raspberry Pi 4
#
from datetime import date
from io import BytesIO
import threading
import queue
import time
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

import google.generativeai as genai
from gtts import gTTS
from pygame import mixer
import speech_recognition as sr

mixer.pre_init(frequency=24000, buffer=2048)
mixer.init()

# add your Google Gemini API key here
my_api_key = " "
if len(my_api_key) < 5:
    print("Please add your Google Gemini API key in the program.\n")
    quit()

# set Google Gemini API key
genai.configure(api_key=my_api_key)

# Important! (2026): 
#   - Use the best updated Gemini model currently available
model = genai.GenerativeModel(
    'gemini-pro',
    generation_config=genai.GenerationConfig(
        candidate_count=1,
        top_p=0.95,
        top_k=40,           # a more conservative value than 64 → better consistency
        max_output_tokens=300,  # for helpful answers
        temperature=0.8,    # greater stability
    )
)

# start the chat model 
chat = model.start_chat(history=[])

today = str(date.today())

# thread 1 for text generation
def chatfun(request, text_queue, llm_done, stop_event):
    full_response = ""
    buffer = ""

    try:
        response = chat.send_message(request, stream=True)

        for chunk in response:
            if stop_event.is_set():
                break
            try:
                if chunk.candidates and chunk.candidates[0].content.parts:
                    text = chunk.candidates[0].content.parts[0].text
                    text = text.replace("*", "").replace("**", "")
                    full_response += text
                    buffer += text

                    while len(buffer) > 180:

                        pos = buffer.rfind(". ") + 2
                        if pos < 2:
                            pos = buffer.rfind(" ") + 1
                        if pos < 2:
                            pos = 180

                        piece = buffer[:pos].strip()
                        if piece:
                            text_queue.put(piece)
                        buffer = buffer[pos:].lstrip()

            except Exception:
                continue

        if buffer.strip():
            text_queue.put(buffer.strip())

        if full_response.strip():
            print(full_response.strip())
            append2log(f"AI: {full_response.strip()}\n")

    except Exception as e:
        print(f"Error en generacion: {e}")
    finally:
        llm_done.set()

# convert "text" to audio file and play back
def speak_text(text):
    mp3file = BytesIO()
    tts = gTTS(text, lang="en", tld='us')
    tts.write_to_fp(mp3file)
    mp3file.seek(0)

    print("AI: ", text)

    try:
        mixer.music.load(mp3file, "mp3")
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.2)
    except KeyboardInterrupt:
        mixer.music.stop()
    finally:
        mp3file = None

# thread 2 for tts
def text2speech(text_queue, tts_done, llm_done, audio_queue, stop_event):
    time.sleep(0.8)

    while not stop_event.is_set():
        try:
            text = text_queue.get(timeout=1.2)
            if not text:
                continue

            try:
                mp3file = BytesIO()
                tts = gTTS(text, lang="en", tld='us')
                tts.write_to_fp(mp3file)
                mp3file.seek(0)
                audio_queue.put(mp3file)
            except Exception:
                continue

            text_queue.task_done()

        except queue.Empty:
            if llm_done.is_set():
                tts_done.set()
                break

# thread 3 for audio playback
def play_audio(audio_queue, tts_done, stop_event):
    while not stop_event.is_set():
        try:
            mp3audio = audio_queue.get(timeout=1.5)
            mp3audio.seek(0)

            mixer.music.load(mp3audio, "mp3")
            mixer.music.play()

            while mixer.music.get_busy():
                time.sleep(0.2)

            audio_queue.task_done()

        except queue.Empty:
            if tts_done.is_set():
                break

# save conversation to a log file
def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a", encoding='utf-8') as f:
        f.write(text + "\n")

# define default language to work with the AI model
slang = "en-EN"

# Main function
def main():
    global today, slang

    rec = sr.Recognizer()
    mic = sr.Microphone()

    rec.dynamic_energy_threshold = True
    rec.energy_threshold = 350

    sleeping = True

    while True:
        with mic as source:
            rec.adjust_for_ambient_noise(source, duration=0.6)
            try:
                print("Listening ...")
                audio = rec.listen(source, timeout=12, phrase_time_limit=18)
                text = rec.recognize_google(audio, language=slang)

                if not text.strip():
                    continue

                print(f"You: {text}\n")

                if sleeping:
                    if "rasby" in text.lower(): # name bot!
                        request = text.lower().split("rasby", 1)[1].strip()
                        sleeping = False

                        append2log("_" * 40)
                        today = str(date.today())

                        if len(request) < 2:
                            speak_text("Hi there, how can I help?")
                            continue
                    else:
                        continue
                else:
                    request = text.lower()
                    if "that's all" in request:
                        append2log(f"You: {request}\n")
                        speak_text("Bye now")
                        append2log("AI: Bye now.\n")
                        sleeping = True
                        continue

                    if "rasby" in request:
                        request = request.split("rasby", 1)[1].strip()

                if not request:
                    continue

                append2log(f"You: {request}\n")

                text_queue = queue.Queue()
                audio_queue = queue.Queue()

                llm_done = threading.Event()
                tts_done = threading.Event()
                stop_event = threading.Event()

                llm_thread = threading.Thread(
                    target=chatfun,
                    args=(request, text_queue, llm_done, stop_event)
                )
                tts_thread = threading.Thread(
                    target=text2speech,
                    args=(text_queue, tts_done, llm_done, audio_queue, stop_event)
                )
                play_thread = threading.Thread(
                    target=play_audio,
                    args=(audio_queue, tts_done, stop_event)
                )

                llm_thread.start()
                tts_thread.start()
                play_thread.start()

                llm_done.wait()
                llm_thread.join()

                tts_done.wait()
                audio_queue.join()

                stop_event.set()
                tts_thread.join()
                play_thread.join()

                print()

            except Exception:
                continue

if __name__ == "__main__":
    main()
