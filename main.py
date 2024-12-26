import tkinter as tk
import pyaudio
import threading
import wave
from datetime import datetime
from faster_whisper import WhisperModel
from fastapi import FastAPI


class StartStopApp:
    
    def __init__(self, root):   #The method __init__(self, root) is a constructor in Python.self is a current instance of a class.
        self.running = False      # this varibale is used To track the current state, is it running state or not
        self.audio_thread = None 
        self.stream = None
        self.p = None
        self.frames = []  # Store audio frames to save later
        self.model = WhisperModel("base")  # Load the Whisper model

        # Start Button
        self.start_button = tk.Button(root, text="Start", width=10, command=self.start)
        self.start_button.pack(pady=10)

        # Stop Button
        self.stop_button = tk.Button(root, text="Stop", width=10, command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Status Label
        self.label = tk.Label(root, text="Status: Stopped", font=("Arial", 12))
        self.label.pack(pady=20)

        # Transcript Label (this will show the generated transcript)
        self.transcript_label = tk.Label(root, text="Transcript: ", font=("Arial", 12), wraplength=300)
        self.transcript_label.pack(pady=20)


    def start(self):  #start method is triggered,It's main job is to It begins capturing live audio data from the microphone in a separate thread.
        if not self.running:  #Checks if the audio stream is not currently running
            self.running = True #audio streaming process has started.
            self.label.config(text="Status: Running")    
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)  #Enable the stop button

            # Reset the frames
            self.frames = []

            # Start audio stream in a separate thread
            self.audio_thread = threading.Thread(target=self.audio_stream, daemon=True)
            self.audio_thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.label.config(text="Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            # Stop the audio stream
            if self.stream and self.p:   #if both self.stream and self.p are not None (or not undefined)
                self.stream.stop_stream()  #audio stream that is created
                self.stream.close()
                self.p.terminate()

            # Save audio data to a .wav file
            # self.save_audio_to_wav()

              # Save audio data to a .wav file
            output_filename = self.save_audio_to_wav()

            # Generate the transcript from the saved audio
            transcript = self.transcribe_audio(output_filename)

            # Print the transcript to the console (optional)
            print("Transcript:", transcript)

            # Update the transcript label with the generated text (ensure it's done in the main thread)
            self.update_transcript_label(transcript)

       


    def audio_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,  # 16-bit resolution
                                  channels=1,              # Mono audio
                                  rate=44100,              # Sampling rate
                                  input=True,              # Input mode
                                  frames_per_buffer=1024)  # Buffer size

        while self.running:
            audio_data = self.stream.read(1024, exception_on_overflow=False)
            self.frames.append(audio_data)  # Append audio data to frames list
            print(f"Streaming audio chunk: {len(audio_data)} bytes")  # Simulated streaming

    def save_audio_to_wav(self):
        # Define the output filename
       
        # Get the current date and time for the filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Define the output filename with the current timestamp
        output_filename = f"audio_{timestamp}.wav"

        
        # Save the captured frames to a .wav file
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono channel
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))  # 16-bit resolution
            wf.setframerate(44100)  # Sampling rate
            wf.writeframes(b''.join(self.frames))  
     
        print(f"Audio saved as {output_filename}")
        return output_filename
    

    

    def transcribe_audio(self,audio_file):
        # Load the Whisper model
        model = WhisperModel(f"medium.en", device="cpu", compute_type="int8")
        # Transcribe the audio file
        segments, info = model.transcribe(audio_file, beam_size=5)
    
        # Combine transcription from all segments
        transcription = ' '.join(segment.text for segment in segments)
        return transcription
    

    def update_transcript_label(self, transcript):
        """Updates the transcript label from the main thread"""
        # Use root.after() to ensure that the label is updated in the main thread
        root.after(0, self.transcript_label.config, {"text": f"Transcript: {transcript}"})
   



app = FastAPI()


# Create the main window
root = tk.Tk()
root.title("Start/Stop Buttons")
root.geometry("200x200")

app = StartStopApp(root)

# Run the application
root.mainloop()
