import requests
import sys
import os

def print_usage():
    print('Usage: python download_html.py [url to html] (-o outputfilename)(optional)')

if len(sys.argv) < 2:
    print_usage()
    sys.exit()

outputfilename = ''

if len(sys.argv) == 4:
    if sys.argv[2] == '-o':
        outputfilename = sys.argv[3]
    else:
        print_usage()
        sys.exit()

url = sys.argv[1]

if not url.startswith('http'):
    a = input('URL does not start with \'http\', still proceed?(N/y) ==> ')
    if a.lower() == 'n':
        sys.exit()
    elif a.lower() != 'y':
        print('Cannot recognize the input')
        sys.exit()

if outputfilename == '':
    outputfilename = url.split('/')[-1]

if os.path.exists(outputfilename):
    a = input(f'{outputfilename} already exists! Overwrite it?(N/y) ==> ')
    if a.lower() == 'n':
        sys.exit()
    elif a.lower() != 'y':
        print('Cannot recognize the input')
        sys.exit()

html = requests.get(url).text

fout = open(outputfilename, 'w', encoding='utf-8')

fout.write(html)

print(f'成功寫到 {outputfilename} ')
