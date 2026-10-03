# Remember to use python version 313
from os import listdir
from os.path import isfile, join
import os
#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
#from pygame import mixer
import io
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
#from pytubefix import YouTube
#from pytubefix.cli import on_progress
#from pytubefix import Playlist
from yt_dlp import YoutubeDL
import time
from random import randrange

def Download_videos(url_list):
    res_select = res_cb_var.get().lower()

    if res_select == 'max':
        options = {
            'format':' bestvideo+bestaudio'
        }
    else:
        options = {
            'format':f'bv[height<={res_select}]+ba/b[height<={res_select}]'
        }

    try:
        with YoutubeDL(options) as ydl:
            for url in url_list:
                ydl.download(url)
                time.sleep(randrange(5, 7))

    except Exception as e:
        print(str(e))
        return 'fetching info fail'

def Download_audios(url_list):
    try:
        with YoutubeDL({'extract_audio': True, 'format': 'bestaudio'}) as ydl:
            for url in url_list:
                #info_dict = ydl.extract_info(link, download = True)
                #video_title = info_dict['title']
                #print(video_title)
                ydl.download(url)    
                print("Successfully Downloaded - see local folder")
    
    except Exception as e:
        print(str(e))
        return 'fetching info fail'

#def Span_playlist_button_click():
#    cursor_pos = text_widget.index(INSERT)
#    current_line_number = cursor_pos.split('.')[0]
#    line_start_pos = current_line_number + '.0'
#    next_line_start_pos = str(int(current_line_number)+1) + '.0'
#    playlist_url = text_widget.get(line_start_pos, next_line_start_pos).rstrip('\r\n')
#    playlist = Playlist(playlist_url)
#
#    text_widget.delete(line_start_pos, next_line_start_pos+'-1c')
#
#    for url in playlist.video_urls:
#        text_widget.insert(INSERT, url+'\n')
#
#    return

def Download_button_click():
    media_format = media_cb_var.get().lower()

    #if media_format == 'video':
    #    target_dir = 'video_files'
    #elif media_format == 'audio':
    #    target_dir = 'audio_files'
    #else:
    #    messagebox.showinfo('提示', 'media format 請選擇 video 或 audio')
    #    return

    #if not os.path.exists(target_dir):
    #    os.mkdir(target_dir)

    textContent = text_widget.get('1.0', END)
    input_buf = io.StringIO(textContent)
    output_buf = io.StringIO()

    url_list = []

    for line in input_buf:
        url = line.strip().rstrip('\r\n')
        if len(url) > 0:
            if ' ' not in url:
                url_list.append(url)
                #tmp_info = url + ' : download ' + media_format + ' ' + result + '\n'
                #output_buf.write(tmp_info)
                #print(tmp_info)
            else:
                print('url format invalid : ' + url)

    if media_format == 'video':
        Download_videos(url_list)
    elif media_format == 'audio':
        Download_audios(url_list)
    else:
        messagebox.showinfo('提示', 'media format 請選擇 video 或 audio')
        return

    #output_buf.seek(0)

    #text_widget.delete('1.0', END)

    #for line in output_buf:
    #    text_widget.insert(END, line)

    #mixer.music.load('C:\\Users\\KevinLin\\Music\\fuzzy ending riff.mp3')
    #mixer.music.play(5)
    messagebox.showinfo('提醒', '任務結束')
    #mixer.music.stop()

#def comboSelected(event):
#    print('Combobox is selected.')

root = Tk()
root.title('小程式')

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
w = int(screenWidth * 0.8)
h = int(screenHeight * 0.8)
x = (screenWidth - w) / 2
y = (screenHeight - h) / 2
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

toolbar = Frame(root)
toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

#media_label = Label(toolbar, text='media type')
#media_entry = Entry(toolbar)
#media_entry.insert(0, 'video')

#media_entry.pack(side=RIGHT, padx=(0, 10), pady=3)
#media_label.pack(side=RIGHT, padx=2, pady=3)

#btn = Button(toolbar, text='Span playlist', command = Span_playlist_button_click)
#btn.pack(side=RIGHT, padx=(0, 500), pady=3)

btn2 = Button(toolbar, text='Download', command = Download_button_click)
btn2.pack(side=RIGHT, padx=(0, 200), pady=3)

media_cb_var = StringVar()
media_cb = Combobox(toolbar, textvariable=media_cb_var)
media_cb['value'] = ('video', 'audio')
media_cb.current(0)
#var.set('video') 
#media_cb.bind('<<ComboboxSelected>>', comboSelected)
media_cb.pack(side=RIGHT, padx=(0, 200), pady=3)

res_cb_var = StringVar()
res_cb = Combobox(toolbar, textvariable=res_cb_var)
res_cb['value'] = ('max', '1080', '720', '480', '360')
res_cb.current(0)
#var.set('video') 
#res_cb.bind('<<ComboboxSelected>>', comboSelected)
res_cb.pack(side=RIGHT, padx=(0, 200), pady=3)

xscrollbar = Scrollbar(root, orient=HORIZONTAL)
yscrollbar = Scrollbar(root)
text_widget = Text(root, wrap='none', bg='black', fg='lightgray', font='Consolas 16', undo=True, blockcursor=True)
text_widget.config(insertbackground='white')

xscrollbar.pack(side=BOTTOM, fill=X)
yscrollbar.pack(side=RIGHT, fill=Y)
text_widget.pack(fill=BOTH, expand=True)

xscrollbar.config(command=text_widget.xview)
yscrollbar.config(command=text_widget.yview)
text_widget.config(xscrollcommand=xscrollbar.set)
text_widget.config(yscrollcommand=yscrollbar.set)
text_widget.focus_set()

#mixer.init()

root.mainloop()
