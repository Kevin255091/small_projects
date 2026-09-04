import io
import os
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

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

def main():
    root.mainloop()

def search_btn_click():
    cursor_pos = text_widget.index(INSERT)
    line_start_pos = cursor_pos.split('.')[0] + '.0'
    buf = io.StringIO(text_widget.get(line_start_pos, END))
    threshold = 20
    for line in buf:
        try:
            threshold = int(line.strip().rstrip('\r\n'))
            break
        except:
            continue

    text_widget.insert(INSERT, '\n==========================================================\n')
    text_widget.insert(INSERT, '檔案數量超過' + str(threshold) + '個的目錄：\n')

    global working_directory

    match_count = 0
    for rt, dirs, files in os.walk(working_directory, topdown=True):
        dirs[:] = [d for d in dirs if search_directory_or_not(d)]
        if len(files) >= threshold:
            text_widget.insert(INSERT, os.path.abspath(rt) + '\n')
            match_count += 1

    if match_count == 0:
        text_widget.insert(INSERT, '查無結果\n')
    text_widget.insert(INSERT, '==========================================================\n')

    text_widget.mark_set(INSERT, cursor_pos)

    hint_info_label.config(text='搜尋完成')
    root.after(2000, hint_info_label_refresh)

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

def search_directory_or_not(directory):
    global ignore_directories

    if directory in ignore_directories:
        return False

    if directory[0] == '.':
        return False

    return True

def strip_outrange_char(words):
    char_list = [words[j] for j in range(len(words)) if ord(words[j]) in range(65536)]
    s=''
    for c in char_list:
        s=s+c
    return s


if __name__ == '__main__':
    root = Tk()
    root.title('目錄檔案數量搜尋小程式')

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
        
    ignore_directories = set(['AppData', 'Roaming', 'eclipse', 'Poderosa', 'CondorcetWinner', 
        'Searches', 'cmder_mini', 'VirtualBox VMs'])

    working_directory_label = Label(directory_info_bar, text=working_directory, font=(None, font_size))
    working_directory_label.pack(side=RIGHT, padx=3, pady=3)

    change_dir_btn = Button(directory_info_bar, text='Change directory', font=(None, font_size), command=change_directory_click)
    change_dir_btn.pack(side=RIGHT, padx=3, pady=3)

    change_to_home_btn = Button(directory_info_bar, text='Change to home directory', 
            font=(None, font_size), command=change_to_home_directory_click)
    change_to_home_btn.pack(side=RIGHT, padx=3, pady=3)

    toolbar = Frame(root)
    toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

    instruct_info = '請在下面的 text area 輸入檔案數量門檻值，並按下 search 按鈕'
    instruct_info_label = Label(toolbar, text=instruct_info, font=(None, font_size))
    instruct_info_label.pack(side=LEFT, padx=2, pady=3)

    #search_btn = Button(toolbar, text='search', font=(None, font_size), command=search_btn_click)
    #search_btn.pack(side=LEFT, padx=5, pady=3)

    search_btn = Button(toolbar, text='search', font=(None, font_size), command=search_btn_click)
    search_btn.pack(side=LEFT, padx=5, pady=3)

    #search_recursively_btn = 
    #Button(toolbar, text='search recursively', font=(None, font_size), command=search_recursively_btn_click)
    #search_recursively_btn.pack(side=LEFT, padx=5, pady=3)

    hint_info_label = Label(toolbar, text='      ', font=(None, 12))
    hint_info_label.pack(side=LEFT, padx=5, pady=3)

    xscrollbar = Scrollbar(root, orient=HORIZONTAL)
    yscrollbar = Scrollbar(root)
    text_widget = Text(root, wrap='none', bg='lightgreen', font='Consolas 16', undo=True, blockcursor=True)

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

    main()
