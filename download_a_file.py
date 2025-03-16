import requests
from os import listdir
from os.path import isfile, join
import os
import sys
import subprocess
import time
from random import randrange
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
import queue
import threading

def Download(url, output_fname=None, verify_opt=True):
    if output_fname == None:
        filename = url.split('/')[-1]
    else:
        filename = output_fname

    if os.path.exists(filename) and os.path.isfile(filename):
        i = filename.rfind('.')
        filename = filename[:i] + '(1)' + filename[i:]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    with requests.get(url, stream=True, headers=headers, verify=verify_opt) as response:
        #response.raise_for_status()
        if not response.ok:
            print(response)
            return 'failure'

        with open(filename, 'wb') as handle:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    handle.write(chunk)

        print(f'{filename} is saved.')

        return 'success'


if len(sys.argv) < 2 or len(sys.argv) > 5:
    print('Usage: python download_a_file.py [file url] (-o [output filename])(optional) (--verify==false)(optional)')
    print(f'The length of arguments is {len(sys.argv)}.')
    sys.exit()

file_url = sys.argv[1]

if not file_url.startswith('https://'):
    print('File url does not start with \'https://\'.')
    print('File url : ' + file_url)
    r = input('Proceed?(Y/n) ==> ')

    if r != 'Y' and r != 'y':
        sys.exit()

output_filename = None
verify_opt = True

argv_len = len(sys.argv)
if argv_len > 2:
    i = 2
    while i < argv_len:
        if sys.argv[i] == '-o':
            output_filename = sys.argv[i+1]
            i += 2
            continue
        if sys.argv[i].startswith('--verify=='):
            f = sys.argv[i].split('==')[1].lower()
            if f == 'false':
                verify_opt = False
            elif f != 'true':
                print('Do you mean \'--verify==false\'? Please try again')
                sys.exit()
            i += 1
            continue
        print(f'Cannot recognize {sys.argv[i]}.')
        print_usage()
        sys.exit()


r = Download(file_url, output_filename, verify_opt)

if r != 'success':
    print('下載失敗')
    sys.exit()

print('下載成功')

#play some sound here

print('程式即將結束')

