import ctypes
import io
from io import BytesIO
import sys
import time
import struct
import msvcrt
from urllib.parse import unquote
import vlc #vlc 一定要最後 import, 和 pointer有關, 詳細原因不清楚


MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64))
MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)


def print_usage():
    print('Usage: python my_video_player.py [video file]')
    print('After the media is playing,')
    print('input [space] to pause or continue playing,')
    print('input [p] to play again,')
    print('input [q] to stop and exit the function.')


def media_open_cb(opaque, data_pointer, size_pointer):
    data_pointer.contents.value = opaque
    size_pointer.contents.value = sys.maxsize
    return 0


def media_read_cb(opaque, buffer, length):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    new_data = stream.read(length)
    for i in range(len(new_data)):
        buffer[i]=new_data[i]
    return len(new_data)


def media_seek_cb(opaque, offset):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    stream.seek(offset)
    return 0


def media_close_cb(opaque):
    stream=ctypes.cast(opaque,ctypes.POINTER(ctypes.py_object)).contents.value
    stream.close()


callbacks = {
    'open': MediaOpenCb(media_open_cb),
    'read': MediaReadCb(media_read_cb),
    'seek': MediaSeekCb(media_seek_cb),
    'close': MediaCloseCb(media_close_cb)
}

#def MediaPlayerTimeChanged(event, userData):
#  print( event.u.new_time)

def play_stream(stream, stream_name):
    instance = vlc.Instance()
    player = instance.media_player_new()
    #vlc_events = player.event_manager()
    #vlc_events.event_attach(vlc.EventType.MediaPlayerTimeChanged, MediaPlayerTimeChanged, None)
    #media = instance.media_new_callbacks(callbacks['open'], callbacks['read'], callbacks['seek'], callbacks['close'], ctypes.cast(ctypes.pointer(ctypes.py_object(stream)), ctypes.c_void_p))
    media = instance.media_new_callbacks(callbacks['open'], callbacks['read'], callbacks['seek'], None, ctypes.cast(ctypes.pointer(ctypes.py_object(stream)), ctypes.c_void_p))
    player.set_media(media)

    print('Now is playing ')
    print(stream_name)
    #print('')

    #player.audio_set_volume(100)
    player.play()
    player.pause()
    player.stop()
    time.sleep(0.1) 

    stream.seek(0)
    player.set_position(0)
    player.play()

    mode = 'play'
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
                stream.seek(0)
                #player.set_media(media)
                #player.stop()
                player.set_position(0)
                player.play()

            elif key == 'n':
                player.stop()
                return 'n'

            elif key == 'q':
                player.stop()
                return 'q'
        else:
            if str(player.get_state()) == 'State.Ended':
                player.stop()
                return 'n'
            time.sleep(0.5)

def print_secs_in_readable_form(secs):
    if secs < 60:
        print(f'{secs} 秒')
        return

    mins = secs // 60
    remain_secs = secs % 60

    if mins < 60:
        print(f'{mins} 分 {remain_secs} 秒')
        return

    hours = mins // 60
    remain_mins = mins % 60

    print(f'{hours} 小時 {remain_mins} 分 {remain_secs} 秒')

def print_usage():
    print('Usage: python play_varc.py [varc file]')

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print_usage()
        sys.exit()

    varc_file = sys.argv[1]
    
    if varc_file.split('.')[-1] != 'varc':
        print('It might not be a video archive file. The extension filename should be varc')
        print_usage()
        sys.exit()

    fvarc = open(varc_file, 'rb')
    total_time_in_secs = struct.unpack('!H', fvarc.read(2))[0]
    print('影片總共時長 : ')
    print_secs_in_readable_form(total_time_in_secs)

    while True:
        byte1 = fvarc.read(1)
        
        if byte1 == b'':
            break

        fnb_len = struct.unpack('B', byte1)[0]

        if fnb_len > 127:
            fnb_len -= 128
            file_size_byte_width = 4
        else:
            file_size_byte_width = 3

        fname = fvarc.read(fnb_len).decode('utf-8')

        if file_size_byte_width == 3:
            file_size = struct.unpack('!L', b'\x00' + fvarc.read(3))[0]
        else:
            file_size = struct.unpack('!L', fvarc.read(4))[0]

        stream = BytesIO(fvarc.read(file_size))

        r = play_stream(stream, fname)

        if r == 'q':
            break
