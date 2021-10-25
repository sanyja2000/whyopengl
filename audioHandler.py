import pyaudio, time, numpy as np
from threading import Thread

class AudioHandler:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.fs = 44100
        self.stream = self.p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=self.fs,
                        output=True
                        )#,stream_callback=self.callback)
        self.notes = {}
        self.ch = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        lench = len(self.ch)
        #C1 = 65.40639132514967/2Hz
        curr = 65.40639132514967/2
        for x in range(lench*6):
            self.notes[self.ch[x%lench]+str(int(x/lench)+1)] = round(curr,2)
            curr = curr*2**(1/12)
        self.tempo = 0.5
        self.currentlyPlaying = None
        #self.stream.start_stream()
    def _threadNote(self):
        self.stream.write(self.currentlyPlaying)
    def playNote(self,note, dur, volume=0.5):
        samples = (np.sin(2*np.pi*np.arange(self.fs*dur*self.tempo)*self.notes[note]/self.fs)).astype(np.float32)
        self.currentlyPlaying = volume*samples
        self.music_thread = Thread(target=self._threadNote)
        self.music_thread.start()
    def playSamples(self, samples):
        self.stream.write(samples)
    def playNonBlockNote(self, note, dur, volume=0.5):
        samples = (np.sin(2*np.pi*np.arange(self.fs*dur*self.tempo)*self.notes[note]/self.fs)).astype(np.float32)
        self.currentlyPlaying = samples*volume
    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
    def callback(self,in_data,frame_count,time_info,status):
        data = []#self.currentlyPlaying.tobytes()
        return (data, pyaudio.paContinue)

if __name__== '__main__':
    AH = AudioHandler()

    melody = ["A3","C4","D4","D4","D4","E4","F4","F4","F4","G4","E4","E4","D4","C4","C4","D4"]
    bass = ["E3","A3","G3","G3","G3","A3","C4","C4","C4","D4","A3","A3","G3","A3","A3","G3"]
    dur =  [1 ,1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1 ]
    for n in range(len(melody)):
        AH.playNote(melody[n],dur[n])
        time.sleep(0.1*dur[n]*AH.tempo)

