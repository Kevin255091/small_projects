import io
from tkinter import *
import unicodedata


fullwidth_punc = ['。', '，', '、', '；', '：', '「', '」', '『', '』', '（', '）', \
        '？', '！', '《', '》', '〈', '〉', '．', '～']

halfwidth_punc = ['.', ',', ';', ':', '(', ')', '?', '!', '…', '……', '⋯', '⋯⋯', '—', '~']

punc_shall_not_start = ['。', '.', ',', '，', '、', ';', '；', ':', '：', '」', '』', ')', '）', '?', '？', '!', '！', \
                         '…', '……', '⋯', '⋯⋯', '》', '〉', '．', '—', '～', '~']
def is_CJK(char):
    try:
        if unicodedata.name(char[0]).startswith('CJK'):
            return True
    except Exception as e:
        print(e)
        return True

    return False

def split_to_words(line):
    line = line.strip().rstrip('\r\n')
    word_list = []
    word = ''
    for char in line:
        if is_CJK(char) or char in [' ', '　'] or char in fullwidth_punc: 
            if len(word) > 0:
                word_list.append(word)
                word = ''
            word_list.append(char)
        else:
            word += char

    return word_list

def get_line_width(line_buf_words):
    width = 0
    for w in line_buf_words:
        if is_CJK(w) or w == '　' or w in fullwidth_punc:
            width += 1
        else:
            width += len(w) // 2 + 1
    return width

def typesetting(line_width, first_line_indent_num):
    textContent = text_widget.get('1.0', END)
    input_buf = io.StringIO(textContent)
    output_buf = io.StringIO()
    word_list = []
    line_buf_words = []
    line_total_width = 0
    next_line_total_width = 0

    first_line = True

    for line in input_buf:
        if line[0] in [' ', '　']:
            first_line = True

        word_list = split_to_words(line.strip().rstrip('\r\n'))

        if line.strip().rstrip('\r\n') == '':
            for w in line_buf_words:
                output_buf.write(w)
            output_buf.write('\n')
            line_buf_words.clear()
            output_buf.write('\n')
            first_line = True
            continue

        while len(word_list) > 0:
            if first_line :
                if first_line_indent_num >= line_width:
                    print('indent spaces are too many\nProgram terminated.\n')
                    sys.exit()

                # flush the words in line_buf_words
                if get_line_width(line_buf_words) > 0:
                    for w in line_buf_words:
                        output_buf.write(w)
                    output_buf.write('\n')
                    line_buf_words.clear()

                if first_line_indent_num > 0:
                    #output_buf.write('　' * first_line_indent_num)
                    for i in range(first_line_indent_num):
                        line_buf_words.append('　')
                first_line = False

            if get_line_width(line_buf_words) >= line_width: 
                while word_list[0] in punc_shall_not_start and get_line_width(line_buf_words) > 1:
                    word_list.insert(0, line_buf_words.pop())
                for w in line_buf_words:
                    output_buf.write(w)
                output_buf.write('\n')
                line_buf_words.clear()
            
            while get_line_width(line_buf_words) < line_width and len(word_list) > 0:
                line_buf_words.append(word_list.pop(0))

            if len(word_list) == 0:
                break

        continue

    if get_line_width(line_buf_words) > 0:
        for w in line_buf_words:
            output_buf.write(w)
        output_buf.write('\n')
        line_buf_words.clear()

            
    output_buf.seek(0)

    text_widget.delete('1.0', END)
    
    for line in output_buf:
        text_widget.insert(END, line)

def typesetting_button_click():
    line_width = int(line_width_entry.get())
    typesetting(line_width, int(first_line_indent_num_entry.get()))

def move_to_left_button_click():
    cursor_pos = text_widget.index(INSERT)
    line_start_pos = cursor_pos.split('.')[0] + '.0'
    next_line_start_pos = str(int(line_start_pos.split('.')[0])+1) + '.0'
    line_words = text_widget.get(line_start_pos, next_line_start_pos).strip().rstrip('\r\n').split()
    if len(line_words) == 0:
        hint_info_label.config(text='游標所在行沒有字')
        root.after(2000, hint_info_label_refresh)
        return

    text_widget.delete(line_start_pos, next_line_start_pos + '-1c')

    for word in line_words:
        text_widget.insert(INSERT, word + ' ')


def select_all(event):
    text_widget.tag_add(SEL, '1.0', 'end-1c')
    return 'break'

def hint_info_label_refresh():
    hint_info_label.config(text='')

root = Tk()
root.title('text typesetting 程式')

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
w = int(screenWidth * 0.8)
h = int(screenHeight * 0.8)
x = (screenWidth - w) / 2
y = (screenHeight - h) / 2
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

toolbar = Frame(root)
toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

#btn = Button(root, text='Save', command = saveFile)
#btn.pack(pady=3)

btn  = Button(toolbar, text='Typesetting', command = typesetting_button_click)
btn2 = Button(toolbar, text='Move to left', command = move_to_left_button_click)
line_width_label = Label(toolbar, text='Line width')
line_width_entry = Entry(toolbar)
first_line_indent_num_label = Label(toolbar, text='開頭空格數')
first_line_indent_num_entry = Entry(toolbar)

first_line_indent_num_entry.insert(0, '0')

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    line_width_entry.insert(0, sys.argv[1])
else:
    line_width_entry.insert(0, '50')

line_width_entry.pack(side=RIGHT, padx=10, pady=3)
line_width_label.pack(side=RIGHT, padx=2, pady=3)
btn.pack(side=RIGHT, padx=(0, 500), pady=3)
btn2.pack(side=RIGHT, padx=3, pady=3)
first_line_indent_num_entry.pack(side=RIGHT, padx=3, pady=3)
first_line_indent_num_label.pack(side=RIGHT, padx=2, pady=3)

hint_info_label = Label(toolbar, text='      ', font=(None, 12))
hint_info_label.pack(side=LEFT, padx=2, pady=3)

xscrollbar = Scrollbar(root, orient=HORIZONTAL)
yscrollbar = Scrollbar(root)
text_widget = Text(root, wrap='none', bg='black', fg='lightgray', font='Consolas 16', undo=True, blockcursor=True)
text_widget.config(insertbackground='lightgray')

xscrollbar.pack(side=BOTTOM, fill=X)
yscrollbar.pack(side=RIGHT, fill=Y)
text_widget.pack(fill=BOTH, expand=True)

xscrollbar.config(command=text_widget.xview)
yscrollbar.config(command=text_widget.yview)
text_widget.config(xscrollcommand=xscrollbar.set)
text_widget.config(yscrollcommand=yscrollbar.set)
text_widget.bind("<Control-Key-a>", select_all)
text_widget.bind("<Control-Key-A>", select_all)
text_widget.focus_set()

#str = 'Hello'
#text.insert(END, str)

root.mainloop()
