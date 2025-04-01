import io
from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
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

def undoJob():
    try:
        text_widget.edit_undo()
    except:
        print('先前未有動作')

def redoJob():
    try:
        text_widget.edit_redo()
    except:
        print('先前未有動作')

def openFile():
    global filename
    filename = askopenfilename()
    if filename == '':
        return
    with open(filename, 'r') as f:
        text_widget.delete('1.0', END)
        text_widget.insert(END, f.read())
    root.title(filename)


extensions = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'mp3', 'mp4', 'pdf', 'txt', 'py']

def get_url_parameters(url):
    parameter_strs = url.split('?')[1].split('&')

    params = {}

    for p in parameter_strs:
        param, value = p.split('=')
        params[param] = value

    return params

def Download(url, output_fname=None, verify_opt=True):
    url_without_params = url.split('?')[0]
    url_params = get_url_parameters(url)
    if output_fname == None:
        filename = url_without_params.split('/')[-1]
    else:
        filename = output_fname

    ext_name = filename.split('.')[-1]

    global extensions
    if ext_name not in extensions:
        ans = messagebox.askyesno(title='不認得的副檔名', message = '確定要繼續下載?')
        if not ans:
            return 'failure'

        extensions.append(ext_name)

    if os.path.exists(filename) and os.path.isfile(filename):
        ans = messagebox.askyesno(title='檔名已存在', message = '確定要覆蓋原先的檔案?')

        if not ans:
            return 'failure'

        #i = filename.rfind('.')
        #filename = filename[:i] + '(1)' + filename[i:]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    with requests.get(url_without_params, stream=True, headers=headers, params=url_params, verify=verify_opt) as response:
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


def download_button_click():
    argument = argument_entry.get()

    textContent = text_widget.get('1.0', END)
    input_buf = io.StringIO(textContent)
    output_buf = io.StringIO()

    line_count = 0
    success_count = 0
    for line in input_buf:
        L = line.strip().rstrip('\r\n')

        if L == '':
            continue

        line_count += 1
        if L.startswith('http'):

            if not L.startswith('https'):
                ans = messagebox.askyesno(title=f'{L[:50]}...不是https協定', message = '確定要下載?')
                if not ans:
                    output_buf.write('The following url is skipped. ↓↓↓↓↓↓↓↓↓↓\n')
                    output_buf.write('warning:{L}\n')
                    continue

            r = Download(L)

            if r == 'success':
                output_buf.write(f'{L} downloaded success\n')
                success_count += 1
                continue

            output_buf.write('The following url downloading failed. ↓↓↓↓↓↓↓↓↓↓\n')
            output_buf.write('warning:{L}\n')
            continue

        else:
            print(f'{L} cannot be recognized... Skipped!')
            output_buf.write('warning: cannot recognized {L}\n')

        
    output_buf.seek(0)
    text_widget.delete('1.0', END)

    for line in output_buf:
        if line.startswith('warning:'):
            text_widget.insert(END, line[len('warning:'):], 'warning')
        text_widget.insert(END, line)

    mixer.music.load('C:\\Users\\KevinLin\\Music\\fuzzy ending riff.mp3')
    mixer.music.play(-1)

    if line_count == success_count:
        messagebox.showinfo('提示', '全部下載成功')
        print('Download successfully.')
    else:
        messagebox.showinfo('提醒', '任務結束囉，可能有檔案下載失敗')
    
    mixer.music.stop()


def download_key_pressed(event):
    download_button_click()

def select_all(event):
    text_widget.tag_add(SEL, '1.0', 'end-1c')
    return 'break'


filename = 'Untitled'
root = Tk()
root.title('下載檔案程式')

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
w = int(screenWidth * 0.95)
h = int(screenHeight * 0.8)
x = (screenWidth - w) / 2
y = (screenHeight - h) / 2
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

toolbar = Frame(root)
toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

argument_label = Label(toolbar, text='argument')
argument_entry = Entry(toolbar)
argument_entry.insert(0, 'default value')
argument_entry.pack(side=RIGHT, padx=(0, 10), pady=3)
argument_label.pack(side=RIGHT, padx=2, pady=3)

#btn = Button(toolbar, text='Save', command = saveFile)
#btn.pack(side=RIGHT, pady=3)

button_label_d = Label(toolbar, text='Ctrl-s')
btn = Button(toolbar, text='Download', command = download_button_click)
button_label_d.pack(side=RIGHT, padx=(0, 100), pady=3)
btn.pack(side=RIGHT, padx=(0, 10), pady=3)

xscrollbar = Scrollbar(root, orient=HORIZONTAL)
yscrollbar = Scrollbar(root)
#text_widget = Text(root, wrap='none', bg='lightgreen', font='Consolas 16', undo=True, blockcursor=True)
text_widget = Text(root, wrap='none', bg='black', fg='lightgray', font='Consolas 16', undo=True, blockcursor=True)
text_widget.config(insertbackground='white')
text_widget.tag_config('warning', background="yellow", foreground="red")

xscrollbar.pack(side=BOTTOM, fill=X)
yscrollbar.pack(side=RIGHT, fill=Y)
text_widget.pack(fill=BOTH, expand=True)

xscrollbar.config(command=text_widget.xview)
yscrollbar.config(command=text_widget.yview)
text_widget.config(xscrollcommand=xscrollbar.set)
text_widget.config(yscrollcommand=yscrollbar.set)
text_widget.bind("<Control-Key-a>", select_all)
text_widget.bind("<Control-Key-A>", select_all)
text_widget.bind("<Control-Key-s>", download_key_pressed)
text_widget.bind("<Control-Key-S>", download_key_pressed)
text_widget.focus_set()

#text.mark_set('mark1', '5.0')
#text.mark_set('mark2', '8.0')
#text.tag_add('tag1', 'mark1', 'mark2')
#text.tag_config('tag1', foreground='blue', background='lightyellow', font=Font(16))

root.mainloop()
