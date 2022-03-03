#!/share/apps/nmi_python/miniconda3/bin/python

import os
import sys

from colour import colour


def search_count():
    files = os.listdir()
    cont_list = []
    for file in files:
        file_pre = file.split('-')[0]
        file_count = file.split('-')[-1]
        if file_pre == "CONTCAR":
            try:
                count = int(file_count)
            except ValueError:
                count = 0
            cont_list.append(count)
    try:
        count = max(cont_list)
    except ValueError:
        print(colour('No CONTCAR in current folder!'))
        sys.exit()
    return count


def backupfile(file, count):
    new_file_name = '{}-{}'.format(file, count)
    os.system("cp {} {}".format(file, new_file_name))
    print("{} has been backed up to {}".format(file, new_file_name))


count = search_count()
file_list = ['CONTCAR', 'POSCAR', 'OUTCAR']
for i in file_list:
    backupfile(i, count + 1)

os.system("cp CONTCAR POSCAR")
print(colour("CONTCAR copied to POSCAR", clr='green'))
print(colour("Remember to check INCAR file and submit script before rerun the job.", clr='yellow'))
