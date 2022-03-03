#!/share/apps/nmi_python/miniconda3/bin/python

import os
import sys
import warnings
from colour import colour
from pymatgen.io.vasp import Poscar
from pymatgen.io.cif import CifWriter


def vasp_folder(name):
    os.chdir(name)
    count = 0
    for i in os.listdir():
        if i in ['INCAR', 'POSCAR', 'POTCAR', 'KPOINTS', 'CONTCAR', 'OUTCAR']:
            count += 1
    os.chdir(cwd)
    if count >= 5:
        return True


def trans_format(car_type, name):
    cif_name = name + '_' + car_type[0:3] + '.cif'
    p = Poscar.from_file(car_type)
    w = CifWriter(p.structure)
    w.write_file(cif_name)
    os.popen('cp ' + cif_name + ' ' + car2cif_path)
    global times
    times += 1
    print('{} in {} was transfered to {}'.format(car_type, name, cif_name))


def run(name):
    os.chdir(name)
    # if os.path.isfile(cwd + '/POSCAR') and os.path.exists(cwd + '/POSCAR'):
    #     trans_format('POSCAR', cwd)
    if os.path.isfile('CONTCAR') and os.path.exists('CONTCAR'):
        trans_format('CONTCAR', name)


warnings.filterwarnings('ignore')
cwd = os.getcwd()
times = 0
print('Current working directory is:', cwd)
current_folder = cwd.split(r"/")[-1]
car_folder = current_folder + '-car2cif'
try:
    os.mkdir(car_folder)
except FileExistsError:
    print(colour('Folder {} exists!'.format(car_folder)))
    sys.exit()
car2cif_path = cwd + '/' + car_folder

exclude_folder = input('Specif exclude folders & files (using space to seperate):')
exclude_folders = exclude_folder.split()
run_folder = input('Specif folders to run (default all, using space to seperate):')
run_folders = run_folder.split()
if run_folder:
    folders = run_folders
else:
    folders = os.listdir()
# for root, dirs, files in os.walk(init_cwd):
#     working_path = root
#     run(working_path)
for folder in folders:
    if folder in exclude_folders:
        continue
    if os.path.isfile(folder):
        continue
    if not vasp_folder(folder):
        continue
    if folder.split("-")[-1] == "car2cif":
        continue
    run(folder)
    os.chdir(cwd)
if times == 0:
    print(colour('No CAR file found.'))
    os.popen('rm -r {}'.format(car_folder))
