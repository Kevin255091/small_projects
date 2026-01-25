import io
from tkinter import *

def typesetting(line_width, first_line_indent_num):
    textContent = text_widget.get('1.0', END)
    input_buf = io.StringIO(textContent)
    output_buf = io.StringIO()
    word_list = []
    line_buf_words = []
    line_total_width = 0
    next_line_total_width = 0

    first_line = True
    line_width -= first_line_indent_num
    if line_width < 1:
        print('indent spaces are too many\nProgram terminated.\n')
        sys.exit()

    if first_line_indent_num > 0:
        output_buf.write(' ' * first_line_indent_num)

    for line in input_buf:
        for w in line.strip().rstrip('\r\n').split():
            word_list.append(w)

        if len(word_list) == 0:
            continue

        while len(word_list) > 0:
            w_len = len(word_list[0])
            next_line_total_width = line_total_width

            if w_len > line_width :
                print('The word ' + word_list[0] + ' is too long.\nProgram terminated.\n')
                sys.exit()

            if len(line_buf_words) > 0:
                next_line_total_width += w_len + 1
            else:
                next_line_total_width = w_len

            if next_line_total_width < line_width:
                line_buf_words.append(word_list.pop(0))
                line_total_width = next_line_total_width
                continue
            
            if next_line_total_width > line_width:
                gap_space_num = compute_word_gap(line_buf_words, line_total_width, line_width)
                write_output(line_buf_words, gap_space_num, output_buf)

            elif next_line_total_width == line_width:
                line_buf_words.append(word_list.pop(0))
                line_total_width = next_line_total_width
                gap_space_num = compute_word_gap(line_buf_words, line_total_width, line_width)
                write_output(line_buf_words, gap_space_num, output_buf)

            line_buf_words.clear()
            line_total_width = 0
            
            if not first_line:
                continue

            line_width += first_line_indent_num
            first_line = False

        '''
        if len(line_buf_words) > 0:
            gap_space_num = compute_word_gap(line_buf_words, line_total_width, line_width)
            write_output(line_buf_words, gap_space_num, output_buf)
            line_buf_words.clear()
            line_total_width = 0

        write_output([], [], output_buf)
        '''

    if len(line_buf_words) > 0:
        gap_space_num = compute_word_gap(line_buf_words, line_total_width, line_width)
        write_output(line_buf_words, gap_space_num, output_buf)
    
    output_buf.seek(0)

    text_widget.delete('1.0', END)
    
    for line in output_buf:
        text_widget.insert(END, line)

def write_output(line_buf_words, gap_space_num, output_buf):
    for i in range(len(line_buf_words)):
        output_buf.write(line_buf_words[i] + ' ' * gap_space_num[i])
    output_buf.write('\n')

def compute_word_gap(line_buf_words, line_total_width, line_width):
    word_num = len(line_buf_words)
    gap_space_num = [1] * (word_num)
    gap_space_num[-1] = 0
    word_gap_num = word_num - 1
    if line_total_width < line_width:
        extra_space_num = line_width - line_total_width
        if word_num > 1:
            if extra_space_num < word_gap_num:
                for i in range(extra_space_num):
                    gap_space_num[i] = 2
            else:
                add_space_num = extra_space_num // word_gap_num
                for i in range(word_gap_num):
                    gap_space_num[i] += add_space_num
                extra_space_num %= word_gap_num
                for i in range(extra_space_num):
                    gap_space_num[i] += 1
            return gap_space_num

#            for i in range(word_num - 1):
#                print(line_buf_words[i] + ' ' * gap_space_num[i], end='')
#            print(line_buf_words[-1])

        else:
            gap_space_num[0] = extra_space_num
            return gap_space_num
            #print(line_buf_words[0] + ' ' * extra_space_num)
    else:
        return gap_space_num

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
text_widget = Text(root, wrap='none', bg='lightgray', font='Consolas 16', undo=True, blockcursor=True)

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
