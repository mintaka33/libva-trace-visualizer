import os

trace_files = []

path = './trace'
file_list = os.listdir(path)
for file in file_list:
    print(file.find('thd-'))
    if file.find('thd-') != -1:
        trace_files.append(file)


print('done')


