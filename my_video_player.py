import os
import tkinter
import tkinter.filedialog
from tkinter import messagebox
import sys
import time, vlc
#import keyboard
import msvcrt
from urllib.parse import unquote

def print_usage():
    print('Usage: python my_video_player.py [video file] [--start_time=0.0](optional) [--run_time=60.0](optional)')
    print('After the media is playing,')
    print('input [space] to pause or continue playing,')
    print('input [p] to play again,')
    print('input [q] to stop and exit the function.')


def prompt_file():
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw() # hide window

    file_name = tkinter.filedialog.askopenfilename(parent=top, initialdir=os.getcwd(), 
            filetypes=[("Video files", ".mp4 .mkv .avi")])
    top.destroy()
    #tk_window.destroy() Strangly, it will cause the pygame window not focused.
    return file_name
 
# method to play video
def play_video(video_filename, start_time=0.0, run_time='All'):

    #fname = os.path.join(music_dir, audio_filename)
    fname = video_filename

    if not os.path.exists(fname):
        print(f'{fname} does not exist.')
        return

    instance = vlc.Instance()

    Media = instance.media_new(fname)

    Media.add_option(f'start-time={start_time}')

    if run_time != 'All' :
        Media.add_option(f'run-time={run_time}')

    player = instance.media_player_new()
    player.set_media(Media)
    
     
    print('Now is playing ')
    print(unquote(Media.get_mrl()).split('/')[-1])
    print('')

    if video_filename == 'small_sound.mp3':
        player.audio_set_volume(398)
        time.sleep(0.5)
        print('Hey')
    else:
        player.audio_set_volume(100)

    #volume = player.audio_get_volume()
    #print(volume)

    player.play()
    player.pause()
    time.sleep(0.1)
    player.stop()
    player.play()

    print('Please wait...\n')
    time.sleep(0.5)
    
    duration = player.get_length() #in milliseconds

    print_usage()
    
    mode = 'play'
    #while player.is_playing():
    while True:
        if msvcrt.kbhit():
            #event = keyboard.read_event()
            key = msvcrt.getch().decode('utf-8')

            #if event.event_type != keyboard.KEY_DOWN:
            #    continue

            #key = event.name
            #print(f'Pressed: {key}')

            if key == ' ':
                if player.is_playing():
                    player.pause()
                    #print(player.get_state())
                elif str(player.get_state()) == 'State.Paused':
                    player.play()
                else:
                    player.stop()
                    player.play()

            elif key == 'p':
                #player.stop()
                player.set_position(0)
                player.play()

            elif key == 'n':
                player.stop()
                return 'n'

            elif key == 'b':
                player.stop()
                return 'b'

            elif key == 'q':
                player.stop()
                return 'q'
        else:
            if str(player.get_state()) == 'State.Ended':
                player.stop()
                return
            time.sleep(0.5)


argc = len(sys.argv)

#video_file = sys.argv[1]

start_time = 0.0
run_time = 'All'

for i in range(2, 4):
    if i >= argc:
        break

    if sys.argv[i].startswith('--start_time='):
        start_time = sys.argv[i].split('=')[1]
        start_time = float(start_time)
        continue

    if sys.argv[i].startswith('--run_time='):
        run_time = sys.argv[i].split('=')[1]
        run_time = float(run_time)
        continue

video_file_ext = ['3gp', 'asf', 'avi', 'flv', 'mkv', 'mp4', 'ogg', 'ogm', 'wav', 'es', 'ps', 'ts', 'pva', 'mp3',\
            'aiff', 'mxf', 'vob', 'rm', 'dvb', 'heif', 'avif',\
            'aac', 'ac3', 'alac', 'amr', 'dts', 'xm', 'flac', 'it', 'mace', 'mod', 'ape', 'opus', 'pls', 'qcp',\
            'qdm2', 'qdmc', 'speex', 'tta', 'wma', 'webm']

for r, ds, fs in os.walk('.'):
    i = 0
    fnum = len(fs)
    mode = 'forward'
    while 0 <= i < fnum:
        f = fs[i]

        if f.split('.')[-1].lower() not in video_file_ext:
            if mode == 'forward':
                i = (i+1) % fnum
            else:
                i = (i-1) % fnum
            continue
    
        r = play_video(f, start_time, run_time)

        if r == 'n':
            i = (i+1) % fnum
            mode = 'forward'
            if i == 0:
                print('\n')
                c = input('The playlist has been back to the first one, are you sure to keep playing? (N/y) ==>')
                c = c.lower()
                if not c.startswith('y'):
                    break

            continue

        if r == 'b':
            i = (i-1) % fnum
            mode = 'backward'
            if i == 0:
                print('\n')
                c = input('The playlist has been back to the first one, are you sure to keep playing? (N/y) ==>')
                c = c.lower()
                if not c.startswith('y'):
                    break

            continue

        if r == 'q':
            break

    break


