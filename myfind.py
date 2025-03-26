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

def get_search_keywords():
    cursor_pos = text_widget.index(INSERT)
    line_start_pos = cursor_pos.split('.')[0] + '.0'
    buf = io.StringIO(text_widget.get(line_start_pos, END))
    for line in buf:
        no_newline = line.strip().rstrip('\r\n')
        if len(no_newline) > 0:
            #search_keywords = [ w.lower() for w in re.findall(r'[^,\s]+', no_newline) ]
            search_keywords = parse_keywords(no_newline)
            break
        else:
            hint_info_label.config(text='游標所在行沒有關鍵字可供搜尋')
            root.after(2000, hint_info_label_refresh)
            return []

    return search_keywords

def search_recursively_btn_click():
    search(True)

def search_btn_click():
    search()

def search(recursive=False):
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
    global ignore_extensions

    extname_list = None

    if extn_only_checkbox.get() == True:
        extname_list = [extn.strip() for extn in extname_entry.get().split(',')]
        print(extname_list)

    for rt, dirs, files in os.walk(working_directory, topdown=True):
        dirs[:] = [d for d in dirs if search_directory_or_not(d)]
        for name in files:
            file_ext = None
            if '.' in name:
                file_ext = name.split('.')[-1].lower()
                if file_ext in ignore_extensions:
                    continue
            if extname_list != None and file_ext not in extname_list:
                continue

            fname = os.path.join(rt, name)
            try:
                f = open(fname, 'r', encoding='utf-8')
            except IOError:
                messagebox.showinfo('提示', '無法開啟檔案 ' + fname)
                break

            line_number = 0
            try:
                for line in f:
                    line_number += 1
                    no_newline = line.strip().rstrip('\r\n')
                    text_line = no_newline.lower()
                    keyword_count = 0
                    for keyword in search_keywords:
                        if keyword in text_line:
                            keyword_count += 1
                    if keyword_count == keyword_num:
                        match_count += 1
                        text_widget.insert(INSERT, strip_outrange_char(fname) + ' : ' + str(line_number) + '\n')
                        text_widget.insert(INSERT, strip_outrange_char(no_newline) + '\n\n')
            except Exception as e:
                text_widget.insert(INSERT, 'Exception occured at line ' + str(line_number) + '!\n')
                text_widget.insert(INSERT, 'In file ' + fname + ',\n' + str(e) +'\n')
            f.close()

        if recursive == False:
            break

    if match_count == 0:
        text_widget.insert(INSERT, '查無結果\n')
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

def parse_keywords(line):
    delim = ' ,'
    line = line.strip().rstrip('\r\n')
    line_len = len(line)
    keywords = []
    i = 0
    while i < line_len:
        c = line[i]
        if c not in delim:
            if c != '\"':
                j = i+1
                while j < line_len:
                    c = line[j]
                    if c in delim or c == '\"':
                        break
                    else:
                        j += 1
                keywords.append( line[i:j].lower() )
                i = j
                continue
            else:
                j = i+1
                while j < line_len:
                    if line[j] == '\"':
                        break
                    j += 1
                if j > i+1:
                    keywords.append( line[i+1:j].lower() )
                i = j+1
                continue
        else:
            i += 1
    return keywords


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
ignore_extensions = set(['zip', 'rar', 'jpg', 'bmp', 'png', 'jpeg'])

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

instruct_info = '請在下面的 text area 輸入要搜尋的關鍵字，並按下 search 按鈕'
instruct_info_label = Label(toolbar, text=instruct_info, font=(None, font_size))
instruct_info_label.pack(side=LEFT, padx=2, pady=3)

search_btn = Button(toolbar, text='search content', font=(None, font_size), command=search_btn_click)
search_btn.pack(side=LEFT, padx=5, pady=3)

search_filename_btn = Button(toolbar, text='search filenname recursively', font=(None, font_size), command=search_filename_btn_click)
search_filename_btn.pack(side=LEFT, padx=5, pady=3)

search_recursively_btn = Button(toolbar, text='search content recursively', 
        font=(None, font_size), command=search_recursively_btn_click)
search_recursively_btn.pack(side=LEFT, padx=5, pady=3)

#extension name only checkbox
extn_only_checkbox = BooleanVar()
extn_only_checkbox.set(False)
extn_only_cbtn = Checkbutton(toolbar, text='僅搜尋這些副檔名的檔案', font=(None, font_size), variable=extn_only_checkbox)
extn_only_cbtn.pack(side=LEFT, padx=(2, 0), pady=3)

extname_entry = Entry(toolbar)
extname_entry.insert(0, 'txt, py')
extname_entry.pack(side=LEFT, padx=(2, 0), pady=3)

hint_info_label = Label(toolbar, text='      ', font=(None, 12))
hint_info_label.pack(side=LEFT, padx=5, pady=3)

toolbar2 = Frame(root)
toolbar2.pack(side=TOP, fill=X, padx=2, pady=2)

instruct_info2 = '                                                           '
instruct_info_label2 = Label(toolbar2, text=instruct_info2, font=(None, font_size))
instruct_info_label2.pack(side=LEFT, padx=2, pady=3)

search_all_name_btn = Button(toolbar2, text='search filenname and folder name', font=(None, font_size), command=search_all_name_btn_click)
search_all_name_btn.pack(side=LEFT, padx=5, pady=3)

search_all_name_recursively_btn = Button(toolbar2, text='search filename and folder name recursively', 
        font=(None, font_size), command=search_all_name_recursive_btn_click)
search_all_name_recursively_btn.pack(side=LEFT, padx=5, pady=3)


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
