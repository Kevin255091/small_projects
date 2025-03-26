#當src是資料夾的時候，複製的邏輯和my_backup_manager.py不太一樣，是將整個資料夾複製到目標資料夾底下
import os
import os.path
import sys
from shutil import copyfile
from datetime import datetime
import math

def isNewer(file1, file2):
    mt1 = os.path.getmtime(file1)
    mt2 = os.path.getmtime(file2)

    if mt1 > mt2:
        return True

    return False

def path_name_for_print(path_name):
    if len(path_name) > 2:
        if path_name[0] == '.':
            if path_name[1] == '\\' or path_name[1] == '/':
                return path_name[2:]
    return path_name


file_ignore = ['.gitignore', 'tags']
dir_ignore = ['.git', '__pycache__']

def copy_file(src_file, dst_dir):
    src_file = os.path.abspath(src_file)
    dst_dir = os.path.abspath(dst_dir)

    fname = os.path.basename(src_file)
    src_dir = os.path.dirname(src_file)
    
    fail = False
    if fname not in file_ignore:
        target = os.path.join(dst_dir, fname)

        if (os.path.isfile(target) and isNewer(src_file, target)) or not os.path.isfile(target):
            try:
                copyfile(src_file, target)
            except Exception as e:
                print(str(e))
                fail = True
            if fail:
                print('Fail to copy ' + path_name_for_print(src_file) + ' to ' + path_name_for_print(target))

    elif fname in file_ignore:
        print('Skip ' + src_file + ' because it is in ignore list.\n')

    return


#src might be directory or file
def copy_files_and_subfolders(src, dst_dir, no_recursive=False):  
    if not os.path.exists(src):
        print(src + ' does not exist.')
        sys.exit()

    src = os.path.abspath(src)

    dst_dir = os.path.abspath(dst_dir)

    dst_dir_exists_check = False

    if os.path.isfile(src) == True:
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
            print('create folder ' + path_name_for_print(dst_dir))

        copy_file(src, dst_dir)
        return 

    src_dir = src
    for root, dirs, files in os.walk(src_dir, topdown=True):

        if 'Do_not_copy' in files  or 'do_not_copy' in files:
            print(f'Found \'Do_not_copy\' in folder {src_dir}. So skip...')
            break

        for name in files:
            src_file = os.path.join(root, name)
            if not dst_dir_exists_check and not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
                print('create folder ' + path_name_for_print(dst_dir))
                dst_dir_exists_check = True

            copy_file(src_file, dst_dir)

        if no_recursive == True:
            break

        subfolders_to_copy = []
        for d in dirs:
            if d[0] != '.' and d not in dir_ignore:
                subfolders_to_copy.append(d)
            else:
                print('Skip ' + d + ' because it is in directory ignore list.\n')

        dirs[:] = subfolders_to_copy

        for name in dirs:
            dir_name = os.path.join(root, name)
            target_dir_name = os.path.join(dst_dir, name)
            #if not os.path.isdir(target_dir_name):
            #    os.makedirs(target_dir_name)
            #    eprint('create folder ' + path_name_for_print(target_dir_name))
            copy_files_and_subfolders(dir_name, target_dir_name)

        break


def print_usage():
    print('Usage: python mycopy.py [src directory or src file] [target directory] [--no_recursive](optional)')

def main():
    argv_len = len(sys.argv)
    if argv_len < 3:
        print_usage()
        sys.exit()

    src_arg = sys.argv[1]
    dst_arg = sys.argv[2]

    no_recursive = False

    if argv_len > 3:
        if sys.argv[3] == '--no_recursive':
            no_recursive = True
        else:
            print_usage()
            sys.exit()

    if not os.path.isfile(src_arg):
        if not os.path.isdir(dst_arg):
            os.makedirs(dst_arg)
        new_dst_arg = os.path.join(dst_arg, os.path.basename(src_arg))
        if not os.path.isdir(new_dst_arg):
            os.makedirs(new_dst_arg)
        dst_arg = new_dst_arg

    copy_files_and_subfolders(src_arg, dst_arg, no_recursive)
    return


if __name__ == '__main__':
    main()

