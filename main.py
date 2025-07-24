import pygame
import io
from playsound import playsound
import re
pygame.mixer.init()
from tkinter import Listbox  
from tkinter import *
from tkinter import filedialog, messagebox
import pygame.mixer as mixer
import os
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import time
import threading
from gtts import gTTS
from PIL import Image, ImageTk
import speech_recognition as sr   


mixer.init()    


def play_song(song_name: StringVar, songs_list: Listbox, status: StringVar, song_index: IntVar):
    try:
        selected_song = songs_list.get(song_index.get())
        if selected_song:
            song_name.set(selected_song)
            
            
            speak("Playing music")   
            sanitized_song_name = re.sub(r'[-_]', ' ', selected_song)  
            speak("Now playing " + sanitized_song_name) 
            
            
            time.sleep(5)  
            
            
            mixer.music.load(selected_song)
            mixer.music.play()
            status.set("Playing")
            update_time(song_name, songs_list, song_index)
            update_album_art(selected_song)
            
            
              

    except Exception as e:
        messagebox.showerror("Error", f"Failed to play the song: {e}")


def stop_song(status: StringVar):
    speak("Stopping music")
    mixer.music.stop()
    status.set("Stopped")

def load(listbox: Listbox):
    directory = filedialog.askdirectory(title="Select a Songs Directory")
    if directory:
        os.chdir(directory)
        listbox.delete(0, END)
        for track in os.listdir():
            if track.endswith(".mp3"):
                listbox.insert(END, track)
    speak("Directory loaded")

def pause_song(status: StringVar):
    speak("Pausing music")
    mixer.music.pause()
    status.set("Paused")

def resume_song(status: StringVar):
    speak("Resuming music")
    mixer.music.unpause()
    status.set("Playing")

def shuffle_song(song_name: StringVar, songs_list: Listbox, status: StringVar, song_index: IntVar):
    try:
        speak("shuffling songs")
        total_songs = songs_list.size()
        if total_songs > 0:
            random_index = random.randint(0, total_songs - 1)
            song_index.set(random_index)
            speak("Shuffling songs")
            play_song(song_name, songs_list, status, song_index)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to shuffle songs: {e}")

def next_song(song_name: StringVar, songs_list: Listbox, status: StringVar, song_index: IntVar):
    try:
        speak("Next song")
        total_songs = songs_list.size()
        if total_songs > 0:
            current_index = song_index.get()
            next_index = (current_index + 1) % total_songs
            song_index.set(next_index)
            speak("Next Song")
            play_song(song_name, songs_list, status, song_index)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to go to the next song: {e}")

def previous_song(song_name: StringVar, songs_list: Listbox, status: StringVar, song_index: IntVar):
    try:
        speak("Previous song")
        total_songs = songs_list.size()
        if total_songs > 0:
            current_index = song_index.get()
            prev_index = (current_index - 1) % total_songs
            song_index.set(prev_index)
            speak("Previous song")
            play_song(song_name, songs_list, status, song_index)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to go to the previous song: {e}")

def set_volume(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)

def update_time(song_name: StringVar, songs_list: Listbox, song_index: IntVar):
    if mixer.music.get_busy():
        current_time = mixer.music.get_pos() // 1000
        current_time_formatted = time.strftime('%M:%S', time.gmtime(current_time))
        try:
            song_path = songs_list.get(song_index.get())
            if os.path.exists(song_path):
                song = MP3(song_path)
                total_length = int(song.info.length)
                total_length_formatted = time.strftime('%M:%S', time.gmtime(total_length))
                time_status.set(f"{current_time_formatted} / {total_length_formatted}")
                if mixer.music.get_busy():
                    root.after(1000, lambda: update_time(song_name, songs_list, song_index))
                else:
                    time_status.set("<00:00 / 00:00>")

                
        except Exception:
            time_status.set("<Error Reading Time>")

def update_album_art(song_path: str):
    try:
        tags = ID3(song_path)
        for tag in tags.values():
            if isinstance(tag, APIC):
                image_data = tag.data
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((300, 300))
                album_image = ImageTk.PhotoImage(image)
                album_art_label.config(image=album_image)
                album_art_label.image = album_image
                return
        album_art_label.config(image="", text="No Album Art")
    except Exception as e:
        album_art_label.config(image="", text="Error loading art")


def speak(text):
    def run_speech():
      
        sanitized_text = re.sub(r'[-_]', ' ', text)  # 
        tts = gTTS(text=sanitized_text, lang='en')
        tts.save("temp.mp3")
        playsound("temp.mp3") 
        os.remove("temp.mp3")  
    
    
    threading.Thread(target=run_speech).start()
    

def listen_for_commands():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        try:
            print("Listening for commands...")
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                
            command = recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")

           
            if "play" in command:
                play_song(current_song, playlist, song_status, song_index)
            elif "pause" in command:
                pause_song(song_status)
            elif "stop" in command:
                stop_song(song_status)
            elif "next" in command:
                next_song(current_song, playlist, song_status, song_index)
            elif "previous" in command:
                previous_song(current_song, playlist, song_status, song_index)
            elif "shuffle" in command:
                shuffle_song(current_song, playlist, song_status, song_index)
            elif "load" in command:
                load(playlist)
            elif "resume" in command:
                resume_song(song_status)
            else:
                print("Command not recognized. Try again.")
        
        except sr.UnknownValueError:
            print("Sorry, I did not understand that. Please try again.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")


root = Tk()
root.geometry('1400x600')
root.title('Enhanced Music Player')
root.resizable(0, 0)
root.configure(bg='lightblue')


song_frame = LabelFrame(root, text='Now Playing', bg='lightyellow', width=700, height=150, font=('Arial', 14, 'bold'))
song_frame.place(x=10, y=10)

button_frame = LabelFrame(root, text='Controls', bg='lightgreen', width=700, height=250, font=('Arial', 14, 'bold'))
button_frame.place(x=10, y=170)

listbox_frame = LabelFrame(root, text='Playlist', bg='lightblue', font=('Arial', 14, 'bold'))
listbox_frame.place(x=720, y=10, height=650, width=300)

album_art_frame = Frame(root, bg='white', width=350, height=350)
album_art_frame.place(x=720, y=670)


current_song = StringVar(root, value='<Not selected>')
song_status = StringVar(root, value='<Not Available>')
time_status = StringVar(root, value='<00:00 / 00:00>')
song_index = IntVar(root, value=0)  


playlist = Listbox(listbox_frame, font=('Arial', 12), selectbackground='yellow', bg='lightgrey')
scroll_bar = Scrollbar(listbox_frame, orient=VERTICAL)
scroll_bar.pack(side=RIGHT, fill=BOTH)
playlist.config(yscrollcommand=scroll_bar.set)
scroll_bar.config(command=playlist.yview)
playlist.pack(fill=BOTH, padx=5, pady=5)


Label(song_frame, text='CURRENTLY PLAYING:', bg='lightyellow', font=('Arial', 12, 'bold')).place(x=10, y=30)
Label(song_frame, textvariable=current_song, bg='lightgreen', font=("Arial", 14), width=50, anchor="w").place(x=200, y=30)


album_art_label = Label(album_art_frame, bg='white')
album_art_label.pack(pady=10)


Button(button_frame, text='Pause ⏸️', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: pause_song(song_status)).place(x=10, y=10)
Button(button_frame, text='Stop ⏹️', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: stop_song(song_status)).place(x=150, y=10)
Button(button_frame, text='Play ▶️', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: play_song(current_song, playlist, song_status, song_index)).place(x=290, y=10)
Button(button_frame, text='Resume ▶️', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: resume_song(song_status)).place(x=430, y=10)

Button(button_frame, text='Load Directory 📂', bg='lightgreen', font=("Arial", 12, 'bold'), width=40,
       command=lambda: load(playlist)).place(x=10, y=60)
Button(button_frame, text='Shuffle 🔀', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: shuffle_song(current_song, playlist, song_status, song_index)).place(x=10, y=110)
Button(button_frame, text='Next ⏭️', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: next_song(current_song, playlist, song_status, song_index)).place(x=150, y=110)
Button(button_frame, text='Previous ⏮️', bg='lightgreen', font=("Arial", 12, 'bold'), width=20,
       command=lambda: previous_song(current_song, playlist, song_status, song_index)).place(x=290, y=110)


Label(button_frame, text="Volume:", bg='lightgreen', font=("Arial", 12, 'bold')).place(x=10, y=160)
volume_slider = Scale(button_frame, from_=0, to=100, orient=HORIZONTAL, command=set_volume, bg='lightgreen')
volume_slider.set(50)
volume_slider.place(x=80, y=140)


Label(root, textvariable=time_status, bg='lightyellow', font=('Arial', 12, 'bold')).pack(side=BOTTOM, fill=X)


threading.Thread(target=listen_for_commands, daemon=True).start()


root.mainloop()
