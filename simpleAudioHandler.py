import simpleaudio as sa

class AudioHandler:
    def __init__(self):
        self.sounds_playing = {}
    def playSound(self, filename):
        wave_obj = sa.WaveObject.from_wave_file(filename)
        self.sounds_playing[filename] = wave_obj.play()
    def isStillPlaying(self, filename):
        if filename in self.sounds_playing:
            if self.sounds_playing[filename].is_playing():
                return True
        return False