import os
import os.path
import sys
from datetime import datetime
import math
import shutil

def print_usage():
    print('python MyDir.py [folder name(optional)] [--sort_size(optional)]')


root = ''
sort_size = False

for i in range(1, len(sys.argv)):
    if sys.argv[i] == '--sort_size':
        sort_size = True
    elif os.path.isdir(sys.argv[i]):
        if root != '':
            print('Too many folders are specified!')
            print_usage()
            sys.exit()
        root = sys.argv[i]
    else:
        print(f'Cannot recognize {sys.argv[i]}')
        print_usage()
        sys.exit()


if root == '':
    root = '.'

print()
print(os.path.abspath(root))

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


def print_file_info(filepath, filesize, byte_col_width):
    try:
        mtime = os.path.getmtime(filepath)
    except OSError:
        mtime = 0

    last_modified_time = datetime.fromtimestamp(mtime)
    print(str(last_modified_time)[:19] + '    ', end='')
    if os.path.isdir(filepath):
        print('  <DIR>' + ' ' * byte_col_width + ' ', end='')
    else:
        s = '{0: >' + str(byte_col_width) + '}        '
        print(s.format(str(filesize)), end='')

    s = f'{size_in_print_format(filesize)}'
    ss = s + ' ' * (15-len(s))

    print(f'{ss}', end='')
    print(' ' + os.path.basename(filepath))

def print_dir_info(dirpath, byte_col_width):
    try:
        mtime = os.path.getmtime(dirpath)
    except OSError:
        mtime = 0

    last_modified_time = datetime.fromtimestamp(mtime)
    print(str(last_modified_time)[:19] + '    ', end='')
    print('  <DIR>' + ' ' * byte_col_width + ' ', end='')
    print('{}  '.format('unknown'), end='')
    print('       ' + os.path.basename(dirpath))

if os.path.isfile(root):
    filesize = os.path.getsize(root)
    byte_col_width = len(str(filesize))
    print_file_info(root, filesize, byte_col_width)
    sys.exit()

max_filesize = 0
for current_dir, dirs, files in os.walk(root):
    total_size = 0
    for f in files:
        if root != '.':
            file_name = os.path.join(current_dir, f)
        else:
            file_name = f

        filesize = os.path.getsize(file_name)
        if filesize > max_filesize:
            max_filesize = filesize
        total_size += filesize

    byte_col_width = len(str(max_filesize))

    for d in dirs:
        if root != '.':
            dir_name = os.path.join(current_dir, d)
        else:
            dir_name = d

        print_dir_info(dir_name, byte_col_width)

    print()

    file_size_dict = {}
    for f in files:
        if root != '.':
            file_name = os.path.join(current_dir, f)
        else:
            file_name = f

        if not sort_size:
            print_file_info(file_name, os.path.getsize(file_name), byte_col_width)
        else:
            file_size_dict[file_name] = os.path.getsize(file_name)

    if sort_size:
        sort_dict = dict(sorted(file_size_dict.items(), key=lambda item: item[1]))
        for fname in sort_dict:
            print_file_info(fname, sort_dict[fname] , byte_col_width)

    print()
    print(str(len(files)) + '個檔案')
    print(str(len(dirs)) +  '個目錄')
    print()
    print(f'{os.path.abspath(root)} 總共有 {size_in_print_format(total_size)} ')

    total, used, free = shutil.disk_usage('.')

    print(f'還剩餘 {size_in_print_format(free)} ')

    break
