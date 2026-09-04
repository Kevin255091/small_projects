import io
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
import re
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

def search_directory_or_not(directory):
    global ignore_directories

    if directory in ignore_directories:
        return False

    if directory[0] == '.':
        return False

    return True

def search_recursively_btn_click():
    search(True)

def replace_outrange_char(words, replace_char = '?'):
    #char_list = [words[j] for j in range(len(words)) if ord(words[j]) in range(65536)]
    char_list = []
    for j in range(len(words)):
        if ord(words[j]) in range(65536):
            char_list.append(words[j])
        else:
            char_list.append(replace_char)
    s=''
    for c in char_list:
        s=s+c
    return s


def search_btn_click():
    search()

def size_in_print_format(size):
    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB

    units = [(GB, 'GB'), (MB, 'MB'), (KB, 'KB')]

    for unit in units:
        if size >= unit[0]:
            #return str(size//unit[0]) + '.' + str(math.ceil(10*(size%unit[0])/unit[0])) + ' ' + unit[1]
            point_part_in_3_digits = 1000*(size%unit[0])//unit[0]
            if point_part_in_3_digits % 10 > 4: #四捨五入
                point_part_in_2_digits = (point_part_in_3_digits//10) + 1
            else:
                point_part_in_2_digits = (point_part_in_3_digits//10)

            integer_part = size//unit[0]

            if point_part_in_2_digits > 99 :
                point_part_in_2_digits %= 100
                integer_part += 1

            point_part_str = str(point_part_in_2_digits)

            if len(point_part_str) == 1:
                point_part_str = '0'+point_part_str

            i = 1
            while i >= 0 and point_part_str[i] == '0':
                i -= 1

            if i < 0:
                return f'{integer_part} {unit[1]}'

            return f'{integer_part}.{point_part_str[0:i+1]} {unit[1]}'

    return str(size) + ' bytes'

def search(recursive=False):
    cursor_pos = text_widget.index(INSERT)
    text_widget.insert(INSERT, '搜尋結果：')
    text_widget.insert(INSERT, '\n')

    global working_directory

    extname_list = None

    rank_len = int(rank_list_len_entry.get())

    rank_list = []

    for rt, dirs, files in os.walk(working_directory, topdown=True):
        dirs[:] = [d for d in dirs if search_directory_or_not(d)]
        for name in files:
            fname = os.path.join(rt, name)
            size = os.path.getsize(fname)

            flag = False
            for i in range(len(rank_list)):
                s = rank_list[i][1]
                if size > s:
                    rank_list.insert(i, (fname, size))
                    flag = True
                    if len(rank_list) > rank_len:
                        rank_list.pop()
                    break

            if not flag and len(rank_list) < rank_len:
                rank_list.append((fname, size))

        if recursive == False:
            break

    if len(rank_list) == 0:
        text_widget.insert(INSERT, '查無結果\n')
    else:
        for t in rank_list:
            fname = t[0]
            size  = t[1]
            text_widget.insert(INSERT, replace_outrange_char(fname) + ' : ' + size_in_print_format(size) + '\n')

    text_widget.insert(INSERT, '==========================================================\n')

    text_widget.mark_set(INSERT, cursor_pos)

    hint_info_label.config(text='搜尋完成')
    root.after(2000, hint_info_label_refresh)

def search_filename_btn_click():
    cursor_pos = text_widget.index(INSERT)
    search_keywords = get_search_keywords()
    keyword_num = len(search_keywords)
    text_widget.insert(INSERT, '\n==========================================================\n')
    text_widget.insert(INSERT, '關鍵字為：')
    for w in search_keywords:
        text_widget.insert(INSERT, '\"' + w + '\"  ')
    text_widget.insert(INSERT, '\n\n')

    match_count = 0

    global working_directory

    for rt, dirs, files in os.walk(working_directory, topdown=True):
        dirs[:] = [d for d in dirs if search_directory_or_not(d)]
        for name in files:
            ln = name.lower()
            keyword_count = 0
            for keyword in search_keywords:
                if keyword in ln:
                    keyword_count += 1
            if keyword_count == keyword_num:
                text_widget.insert(INSERT, strip_outrange_char(os.path.join(rt, name)) + ' \n\n')
                match_count += 1

    if match_count == 0:
        text_widget.insert(INSERT, '查無結果\n')
    text_widget.insert(INSERT, '==========================================================\n')

    text_widget.mark_set(INSERT, cursor_pos)

    hint_info_label.config(text='搜尋完成')
    root.after(2000, hint_info_label_refresh)

def search_all_name_btn_click(recursive=False):
    cursor_pos = text_widget.index(INSERT)
    search_keywords = get_search_keywords()
    keyword_num = len(search_keywords)
    text_widget.insert(INSERT, '\n==========================================================\n')
    text_widget.insert(INSERT, '關鍵字為：')
    for w in search_keywords:
        text_widget.insert(INSERT, '\"' + w + '\"  ')
    text_widget.insert(INSERT, '\n\n')

    global working_directory
    match_count = 0
    for rt, dirs, files in os.walk(working_directory, topdown=True):
        dirs[:] = [d for d in dirs if search_directory_or_not(d)]

        for name in dirs:
            ln = name.lower()
            keyword_count = 0
            for keyword in search_keywords:
                if keyword in ln:
                    keyword_count += 1
            if keyword_count == keyword_num:
                text_widget.insert(INSERT, '目錄:\n')
                text_widget.insert(INSERT, strip_outrange_char(os.path.join(rt, name)) + ' \n\n')
                match_count += 1
    
        for name in files:
            ln = name.lower()
            keyword_count = 0
            for keyword in search_keywords:
                if keyword in ln:
                    keyword_count += 1
            if keyword_count == keyword_num:
                text_widget.insert(INSERT, '檔案:\n')
                text_widget.insert(INSERT, strip_outrange_char(os.path.join(rt, name)) + ' \n\n')
                match_count += 1

        if recursive == False:
            break

    if match_count == 0:
        text_widget.insert(INSERT, '無結果\n')

    text_widget.insert(INSERT, '==========================================================\n')

    text_widget.mark_set(INSERT, cursor_pos)

    hint_info_label.config(text='搜尋完成')
    root.after(2000, hint_info_label_refresh)
    

def search_all_name_recursive_btn_click():
    search_all_name_btn_click(True)

def strip_outrange_char(words):
    char_list = [words[j] for j in range(len(words)) if ord(words[j]) in range(65536)]
    s=''
    for c in char_list:
        s=s+c
    return s

def hint_info_label_refresh():
    hint_info_label.config(text='')

def select_all(event):
    text_widget.tag_add(SEL, '1.0', 'end-1c')
    return 'break'

def scroll_down_one_page(event):
    text_widget.yview_scroll(1, PAGES)
    return 'break'

def scroll_up_one_page(event):
    text_widget.yview_scroll(-1, PAGES)
    return 'break'

root = Tk()
root.title('文字搜尋小程式')

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
w = int(screenWidth * 0.9)
h = int(screenHeight * 0.8)
x = int((screenWidth - w) / 2)
y = int((screenHeight - h) / 5)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

font_size = 14

directory_info_bar = Frame(root)
directory_info_bar.pack(side=TOP, fill=X, padx=2, pady=1)

working_directory = os.path.abspath(os.getcwd())
    
ignore_directories = set(['AppData', 'Roaming', 'eclipse', 'Searches', 'cmder_mini', 'VirtualBox VMs'])

working_directory_label = Label(directory_info_bar, text=working_directory, font=(None, font_size))
working_directory_label.pack(side=RIGHT, padx=3, pady=3)

def change_directory_click():
    new_wdir = os.path.abspath(filedialog.askdirectory())
    os.chdir(new_wdir)
    working_directory_label.config(text=new_wdir)
    global working_directory
    working_directory = new_wdir

def change_to_home_directory_click():
    home_dir = 'C:\\Users\\KevinLin'
    os.chdir(home_dir)
    working_directory_label.config(text=home_dir)
    global working_directory
    working_directory = home_dir

change_dir_btn = Button(directory_info_bar, text='Change directory', font=(None, font_size), command=change_directory_click)
change_dir_btn.pack(side=RIGHT, padx=3, pady=3)

change_to_home_btn = Button(directory_info_bar, text='Change to home directory', 
        font=(None, font_size), command=change_to_home_directory_click)
change_to_home_btn.pack(side=RIGHT, padx=3, pady=3)

toolbar = Frame(root)
toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

search_btn = Button(toolbar, text='search files', font=(None, font_size), command=search_btn_click)
search_btn.pack(side=LEFT, padx=5, pady=3)

search_recursively_btn = Button(toolbar, text='search files recursively', 
        font=(None, font_size), command=search_recursively_btn_click)
search_recursively_btn.pack(side=LEFT, padx=5, pady=3)

info = '名次數量'
info_label = Label(toolbar, text=info, font=(None, font_size))
info_label.pack(side=LEFT, padx=2, pady=3)

rank_list_len_entry = Entry(toolbar)
rank_list_len_entry.insert(0, '20')
rank_list_len_entry.pack(side=LEFT, padx=(2, 0), pady=3)

hint_info_label = Label(toolbar, text='      ', font=(None, 12))
hint_info_label.pack(side=LEFT, padx=5, pady=3)

toolbar2 = Frame(root)
toolbar2.pack(side=TOP, fill=X, padx=2, pady=2)

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
text_widget.bind("<Control-Key-a>", select_all)
text_widget.bind("<Control-Key-A>", select_all)
text_widget.bind("<Control-Key-l>", scroll_down_one_page)
text_widget.bind("<Control-Key-L>", scroll_up_one_page)
text_widget.focus_set()

mixer.init()

root.mainloop()
