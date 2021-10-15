import pyaudio
import wave
import sys, select, os
import speech_recognition as sr
from os import startfile
from tkinter import *
from tkinter import scrolledtext
import tkinter as tk
import sounddevice as REC
import threading


global start
start = False
global MasterString
MasterString = ""
global window

global p

global txt

def transcribe(num):
    global MasterString,txt
    # transcribe audio file                                                         
    AUDIO_FILE = "Audio\output" + str(num) + ".wav"

    # use the audio file as the audio source                                        
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file
            try:
                transcription = r.recognize_google(audio)                  

                print("Transcription: " + transcription)
                MasterString += " " + transcription
                print ( "MasterString " + MasterString)

                txt.configure(state="normal")
                txt.insert(INSERT, transcription + " ")
                txt.update()
                txt.configure(state="disabled")

            except Exception:
                print("\n Exception ")


def convertAndTranscribe(j, frames, device_info):
    global p
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 5


    filename = "Audio\output" + str(j) + ".wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(int(device_info["defaultSampleRate"]))
    wf.writeframes(b''.join(frames))
    wf.close()
    print('\nRecording ' + str(j))
    transcribe(j)

def readinAndTranscribe():
    global p

    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 5

    p = pyaudio.PyAudio()

    #Select Device
    print ( "Available devices:\n")
    for i in range(0, p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print ( str(info["index"]) +  ": \t %s \n \t %s" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))
        print ("Number of channels " + str(info['maxInputChannels']))
        pass

    #ToDo change to your device ID
    device_id = 21
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if (dev['name'].strip() == "Line 1 (Virtual Audio Cable)" and p.get_host_api_info_by_index(dev["hostApi"])["name"].strip() == "Windows WASAPI"):
            device_id = dev['index']
            print('\n\ndev_index: \n', device_id)

    print ("Device Id: " + str(device_id))

    device_info = p.get_device_info_by_index(device_id)
    channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=int(device_info["defaultSampleRate"]),
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device_info["index"]
                    )

    frames = []  # Initialize array to store frames

    print('\nRecording', device_id, '...\n')

    # Store data in chunks for 3 seconds
    j= 0
    while j < 10000 and start:
        frames = []
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)
        convertAndTranscribe(j, frames, device_info)
        j = j + 1

    
    print('\nRecording STOP')

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()


def createAndRunWindow():
    global window, txt
    window = Tk()
    window.title("Transcription Buddy")
    window.geometry('745x500')
    txt = scrolledtext.ScrolledText(window,width=60,height=19, font=("Arial", 16))
    txt.grid(column=0,row=0, columnspan=21)
    txt.configure(state="disabled")
    txt.configure(state="normal")
    txt.configure(state="disabled")

    def clicked():
        global start
        start = True
        t4 = threading.Thread(target = readinAndTranscribe)
        t4.start()

    def clickedStop():
        global start
        start = False

    def clickedClear():
        global txt
        txt.configure(state="normal")
        txt.delete('1.0', END)
        txt.configure(state="disabled")

    btn = Button(window, text="Start", command=clicked)
    btn2 = Button(window, text="Stop", command=clickedStop)
    btn3 = Button(window, text="Clear", command=clickedClear)

    btn.grid(column=9, row=1, sticky=tk.N+tk.S+tk.E)
    btn2.grid(column=10, row=1, sticky=tk.N+tk.S)
    btn3.grid(column=11, row=1, sticky=tk.N+tk.S+tk.W)


    window.mainloop()


createAndRunWindow()




