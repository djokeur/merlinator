
from pydub import AudioSegment


def mp3_encode(file):
    
    sound = AudioSegment.from_mp3(file, channels=1)
    sound.sample_width, sound.frame_rate, sound.channels, sound.frame_width
    