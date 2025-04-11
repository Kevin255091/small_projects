import os
import sys
import math

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    WARNING2 = '\033[36m'
    WARNING3 = '\033[34m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_dir_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                try:
                    size = os.path.getsize(fp)
                except:
                    continue
                total_size += size

    return total_size

def size_in_print_format_with_color(size):
    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB

    units = [(GB, 'GB'), (MB, 'MB'), (KB, 'KB')]

    color_code = ''
    for unit in units:
        if size >= unit[0]:
            u = unit[1]

            ns = str(size//unit[0]) + '.' + str(math.ceil(10*(size%unit[0])/unit[0]))

            if u == 'GB':
                return bcolors.FAIL + ns + ' ' + unit[1] + bcolors.ENDC
            elif u == 'MB':
                number = float(ns)
                if number >= 100.0:
                    if number >= 500.0:
                        return bcolors.WARNING + ns + ' ' + unit[1] + bcolors.ENDC
                    else:
                        return bcolors.WARNING2 + ns + ' ' + unit[1] + bcolors.ENDC
                else:
                    return bcolors.OKCYAN + ns + ' ' + unit[1] + bcolors.ENDC
            elif u == 'KB':
                return bcolors.OKGREEN + ns + ' ' + unit[1] + bcolors.ENDC

    return str(size) + ' bytes'

def print_folder_size(target_dir, subfolder_dict, file_dict, total_size=-1):
    subfolder_size = list(subfolder_dict.items())
    file_size = list(file_dict.items())

    subfolder_size.sort(key=lambda tup: tup[1])
    file_size.sort(key=lambda tup: tup[1])

    if total_size == -1:
        total_size = 0
        for sf in subfolder_size:
            total_size += sf[1]
        for f in file_size:
            total_size += f[1]

    print(f'\n{os.path.abspath(target_dir)} 目錄底下有:\n')

    print('-' * 20 + 'Directory' + '-' * 20)
    for tup in subfolder_size:
        print(f'{tup[0]} : {size_in_print_format_with_color(tup[1])}')

    print('\n' + '-' * 20 + 'File' + '-' * 25)
    for tup in file_size:
        print(f'{tup[0]} : {size_in_print_format_with_color(tup[1])}')

    print('\n有 ' + str(len(subfolder_size)) + ' 個子資料夾, ' + str(len(file_size)) + ' 個檔案')
    print(f'總共有 {size_in_print_format_with_color(total_size)}')


def create_snatshot_dict(snatshot_path):
    subfolder_snatshot_dict = {}
    file_snatshot_dict = {}
    with open(snatshot_path, 'r', encoding='utf-8') as fin:
        if fin.readline().startswith('Folders:'):
            while True:
                line = fin.readline().rstrip('\r\n')
                if line[0] == '*':
                    break

                n, s = line.split(':')
                subfolder_snatshot_dict[n] = int(s)

        if fin.readline().startswith('Files:'):
            while True:
                line = fin.readline().rstrip('\r\n')
                if line[0] == '*':
                    break

                n, s = line.split(':')
                file_snatshot_dict[n] = int(s)

    return subfolder_snatshot_dict, file_snatshot_dict

def write_to_snatshot(subfolder_snatshot_dict, file_snatshot_dict, snatshot_path):
    subfolder_size = list(subfolder_snatshot_dict.items())
    file_size = list(file_snatshot_dict.items())

    subfolder_size.sort(key=lambda tup: tup[1])
    file_size.sort(key=lambda tup: tup[1])

    with open(snatshot_path, 'w', encoding='utf-8', newline='\n') as fout:
        fout.write('Folders:\n')
        for sf in subfolder_size:
            fout.write(f'{sf[0]}:{sf[1]}\n')
        fout.write('*************\n')

        fout.write('Files:\n')
        for f in file_size:
            fout.write(f'{f[0]}:{f[1]}\n')
        fout.write('*************\n')

def main():
    target_dir = ''
    revisit = False
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '--revisit':
            revisit = True
        elif target_dir == '':
            target_dir = sys.argv[i]
        else:
            print('Too many folder names')
            print('Usage : python subfolder_size.py [folder_name] [--revisit(optional)]')
            sys.exit()

    if target_dir == '':
        target_dir = '.'

    snatshot_path = os.path.join(target_dir, '.folder_structure')

    if os.path.exists(snatshot_path):
        subfolder_snatshot_dict, file_snatshot_dict = create_snatshot_dict(snatshot_path)
        snatshot_exists = True
        snatshot_modified = False
        if not revisit and os.path.getmtime(target_dir) < os.path.getmtime(snatshot_path):
            print_folder_size(target_dir, subfolder_snatshot_dict, file_snatshot_dict)
            print('以上資料取自.folder_structure快照檔案，僅供參考')
            print('如果一定要重新遍歷計算一遍，請使用 --revisit 參數')
            return
    else:
        snatshot_exists = False


    subfolder_dict = {}
    file_dict = {}
    total_size = 0
    snatshot_ref = False

    for dirpath, dirnames, filenames in os.walk(target_dir):
        for directory in dirnames:
            dirp = os.path.join(dirpath, directory)

            if revisit or not snatshot_exists:
                dir_size = get_dir_size(dirp)
                snatshot_modified = True
            elif directory in subfolder_snatshot_dict and os.path.getmtime(dirp) < os.path.getmtime(snatshot_path):
                dir_size = subfolder_snatshot_dict[directory]
                snatshot_ref = True
            else:
                dir_size = get_dir_size(dirp)
                snatshot_modified = True
            
            subfolder_dict[directory] = dir_size
            total_size += dir_size

        for name in filenames:
            filep = os.path.join(dirpath, name)

            if revisit or not snatshot_exists:
                f_size = os.path.getsize(filep)
                snatshot_modified = True
            elif name in file_snatshot_dict and os.path.getmtime(filep) < os.path.getmtime(snatshot_path):
                f_size = file_snatshot_dict[name]
                snatshot_ref = True
            else:
                f_size = os.path.getsize(filep)
                snatshot_modified = True

            file_dict[name] = f_size
            total_size += f_size

        print_folder_size(target_dir, subfolder_dict, file_dict, total_size)
        break

    if snatshot_exists:
        if len(subfolder_dict) != len(subfolder_snatshot_dict)  or len(file_dict) != len(file_snatshot_dict):
            snatshot_modified = True

    if not snatshot_exists or snatshot_modified:
        write_to_snatshot(subfolder_dict, file_dict, snatshot_path)

    if snatshot_ref:
        print('以上資料大部分取自.folder_structure快照檔案，僅供參考')
        print('如果一定要重新遍歷計算一遍，請使用 --revisit 參數')

    #print(f"{bcolors.HEADER}HEADER{bcolors.ENDC}")
    #print(f'{bcolors.WARNING}Warning{bcolors.ENDC}')
    #print(f'{bcolors.WARNING2}Warning2{bcolors.ENDC}')
    #print(f"{bcolors.OKBLUE}OKBLUE{bcolors.ENDC}")
    #print(f"{bcolors.OKCYAN}OKCYAN{bcolors.ENDC}")
    #print(f"{bcolors.OKGREEN}OKGREEN{bcolors.ENDC}")
    #print(f"{bcolors.UNDERLINE}UNDERLINE{bcolors.ENDC}")

if __name__ == '__main__':
    main()
