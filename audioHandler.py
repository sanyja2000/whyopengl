import pyaudio, time, numpy as np
import wave
from threading import Thread
from functools import partial
import math


def sinwave(range,duration,note):
    fs = 44100
    tempo = 0.5
    return  (np.sin(2*np.pi*np.arange(fs*duration*tempo)*note/fs)).astype(np.float32)

class AudioHandler:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        """
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
        """
        self.currentlyPlaying = {}
        #self.stream.start_stream()
    def isStillPlaying(self,filename):
        if filename in self.currentlyPlaying:
            if self.currentlyPlaying[filename]:
                return True
        return False

    def playSound(self,filename):
        wf = wave.open(filename, 'rb')
        stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)#,stream_callback=self.fileCallback)
        stream.start_stream()
        th = Thread(target=self.playBlockSound, args=(wf,stream,filename))
        th.start()
    
    def playBlockSound(self,wf,stream,filename):
        data = wf.readframes(1024)
        self.currentlyPlaying[filename] = True
        # play stream (3)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(1024)
        self.currentlyPlaying[filename] = False  
        stream.stop_stream()
        stream.close()  



        

if __name__== '__main__':
    AH = AudioHandler()
    
    """
    

    melody = ["A3","C4","D4","D4","D4","E4","F4","F4","F4","G4","E4","E4","D4","C4","C4","D4"]
    bass = ["E3","A3","G3","G3","G3","A3","C4","C4","C4","D4","A3","A3","G3","A3","A3","G3"]
    dur =  [1 ,1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1 ]
    for n in range(len(melody)):
        AH.playNote(melody[n],dur[n])
        time.sleep(0.1*dur[n]*AH.tempo)
    """