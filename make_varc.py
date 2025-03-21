import ctypes
import io
from io import BytesIO
import os
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


def print_usage():
    print('Usage: python make_varc.py -i [video or audio file list](optional) -o [archive file name]')
    print('If no list file is provided, it will archive all the video and audio files in the working directory.')

def play(stream):
    instance = vlc.Instance()
    player = instance.media_player_new()
    #vlc_events = player.event_manager()
    #vlc_events.event_attach(vlc.EventType.MediaPlayerTimeChanged, MediaPlayerTimeChanged, None)
    #media = instance.media_new_callbacks(callbacks['open'], callbacks['read'], callbacks['seek'], callbacks['close'], ctypes.cast(ctypes.pointer(ctypes.py_object(stream)), ctypes.c_void_p))
    media = instance.media_new_callbacks(callbacks['open'], callbacks['read'], callbacks['seek'], None, ctypes.cast(ctypes.pointer(ctypes.py_object(stream)), ctypes.c_void_p))
    player.set_media(media)

    print('Now is playing ')
    print(unquote(media.get_mrl()).split('/')[-1])
    #print('')

    player.play()

    print('Please wait...\n')
    time.sleep(0.3) # player needs time to pause the media info to get the length
    
    duration = player.get_length() #in milliseconds
    print(f'{duration} millisecond(s)')

    print_usage()
    
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

def estimate_total_time(input_file_list):
    duration = 0
    for fname in input_file_list:
        if not os.path.exists(fname):
            print(f'{fname} does not exist.')
            print('Program terminated.')
            sys.exit()

        instance = vlc.Instance()

        Media = instance.media_new(fname)

        player = instance.media_player_new()
        player.set_media(Media)
        
        player.play()

        time.sleep(0.5)
        
        duration += player.get_length() #in milliseconds

        player.stop()

    return duration

def fname_to_byte_string(fname, byte_limit):
    byte_len = 0
    byte_str = b''
    for c in fname:
        cb = c.encode('utf-8')
        if len(cb) + byte_len <= byte_limit:
            byte_len += len(cb)
            byte_str += cb
        else:
            break

    return byte_str

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


def main():
    if len(sys.argv) != 4 and len(sys.argv) != 6:
        print_usage()

    video_file_ext = ['3gp', 'asf', 'avi', 'flv', 'mkv', 'mp4', 'ogg', 'ogm', 'wav', 'es', 'ps', 'ts', 'pva', 'mp3',\
            'aiff', 'mxf', 'vob', 'rm', 'dvb', 'heif', 'avif',\
            'aac', 'ac3', 'alac', 'amr', 'dts', 'xm', 'flac', 'it', 'mace', 'mod', 'ape', 'opus', 'pls', 'qcp',\
            'qdm2', 'qdmc', 'speex', 'tta', 'wma']

    input_file_list = ''
    output_filename = ''

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-i':
            input_file_list = sys.argv[i+1]
            i += 2
            continue
        if sys.argv[i] == '-o':
            output_filename = sys.argv[i+1]
            i += 2
            continue

    if output_filename == '':
        print('[Output archive filename] must provided.')
        print_usage()
        sys.exit()

    if input_file_list == '':
        input_file_list = []
        for r, ds, fs in os.walk('.'):
            for f in fs:
                ext = f.split('.')[-1]
                if ext in video_file_ext:
                    input_file_list.append(f)
            break
    else:
        with open(input_file_list, 'r', encoding='utf-8') as fin:
            input_file_list = []
            for line in fin:
                line = line.rstrip('\r\n')
                if line.split('.')[-1] in video_file_ext:
                    input_file_list.append(line)

    filename_too_long = []
    for f in input_file_list:
        fnb_len = len(os.path.basename(f).encode('utf-8'))
        if fnb_len > 127:
            filename_too_long.append(f)

    if len(filename_too_long) > 1:
        for f in filename_too_long:
            print(f'{f}\'s filename is longer than expected.')
        print('All these files above have longer than expected filenames. Part of the characters will be discarded.')
        r = input('Sure to proceed?(yes/no) ==> ').lower()
        if r == 'no' or r == 'n':
            print('Program terminated!')
            sys.exit()

    if os.path.exists(output_filename):
        print(f'{output_filename} is already existed!')
        r = input('Are you sure to overwrite ? (N/y) ==> ').lower()[0]
        if r == 'n':
            print('Program terminated.')
            sys.exit()

    #Start to parse all the file and estimate the total playing time.
    
    total_time_in_secs = estimate_total_time(input_file_list) // 1000

    print(f'Total time : ')
    print_secs_in_readable_form(total_time_in_secs)

    if total_time_in_secs > (2**16) - 1:
        print(f'Total time is greater than 10 hours')
        print('Too long...')
        print('Program terminated!')
        sys.exit()

    r = input('Sure to make video archive file(varc file) ? (yes/no)').lower()

    if r == 'no' or r == 'n':
        print('Program terminated!')
        sys.exit()

    if r != 'yes' and r != 'y':
        print(f'Cannot understand {r}')
        sys.exit()

    with open(output_filename, 'wb') as fout:
        fout.write(struct.pack('!H', total_time_in_secs))

        for f in input_file_list:
            fsize = os.path.getsize(f)
                
            basename = os.path.basename(f)
            fnb = fname_to_byte_string(basename, byte_limit=127)
            fnb_len_b = struct.pack('B', len(fnb))

            if fsize <= (2**24) - 1: #3 bytes are enough to record the file size
                fout.write(fnb_len_b)
            else: # It needs 4 bytes to record the file size, so using the most significant bit of file size to tell
                fout.write(fnb_len_b | b'\x80')

            fout.write(fnb) # write the filename size byte string

            fsize_b = struct.pack('!L', fsize)
            if fsize <= (2**24) - 1: #3 bytes are enough to record the file size
                fout.write(fsize_b[-3:])
            else:
                fout.write(fsize_b)

            fin = open(f, 'rb')
            fout.write(fin.read())
            fin.close()


if __name__ == '__main__':
    try:
        #path = "two_mp4_files.marc"
        #stream = open(path, 'rb')
        #bs1 = stream.read(295064)
        #bs2 = stream.read(1422583)
        #stream1 = BytesIO(bs1)
        #stream2 = BytesIO(bs2)
        main()
        #main(stream2)
    except IndexError:
        print('Usage: {0} <path>'.format(__file__))
        sys.exit(1)
