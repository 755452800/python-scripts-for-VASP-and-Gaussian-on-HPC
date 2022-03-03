#!/share/apps/nmi_python/miniconda3/bin/python

"""
@Author: steven
Date: Sun Jul 11 12:45:28 CST 2021
Last modified on : Sun Jul 11 21:34:02 CST 2021

1. only os.chdir() can change the working directory in python scripts, os.system('cd ') won't work
2. to extract float number using grep with regx, it should be grep -P "\d*\.\d+" -o, more in
    https://github.com/vieyahn2017/shellV/issues/45
3. remember to use if xxx in []: rather than if xxx == yyy or zzz
4. cell object in ase module: https://wiki.fysik.dtu.dk/ase/ase/cell.html
                              https://wiki.fysik.dtu.dk/ase/ase/geometry.html

"""
import os
import sys
from colour import colour
from ase.io import read as poscar_reader
from ase.cell import Cell

test_choice = input('Specify test:\n1. ENCUT\n2. SIGMA0\n3. SIGMA1\n4. KPOINTS\n5. lattice\n')
test_dict = {"1": "ENCUT", "2": "SIGMA0", "3": "SIGMA1", "4": "KPOINTS", "5": "lattice"}
try:
    test = test_dict[test_choice]
except KeyError:
    print(colour("Wrong input,try again"))
    sys.exit()

encut_gradient = [450, 500, 550, 600, 650, 700, 750]
sigma0_gradient = [0.02, 0.03, 0.04, 0.05, 0.06]
sigma1_gradient = [0.15, 0.18, 0.2, 0.22, 0.25]
kpoints_gradient = ['2 2 1', '3 3 1', '4 4 1', '5 5 1']
lattice_gradient = [-0.15, -0.1, 0, 0.1, 0.15]
grad_dict = {"ENCUT": encut_gradient, "SIGMA0": sigma0_gradient, "SIGMA1": sigma1_gradient, "KPOINTS": kpoints_gradient,
             "lattice": lattice_gradient}

wd = os.getcwd()
print("Current working directory is: {}".format(colour(wd, clr='green')))

if os.path.exists('tmpl'):
    print('Template file folder: {}'.format(colour('tmpl', clr='green')))
else:
    print(colour('No template file folder!'))
    sys.exit()


def lattice(i):
    poscar = poscar_reader("POSCAR")
    cell = poscar.get_cell()
    a = list(cell.lengths())[0]
    c = list(cell.lengths())[2]
    a = a + i
    new_cell = [a, a, c] + list(cell.angles())
    new_cell_par = Cell.fromcellpar(new_cell)
    line_0 = '\t'.join([str(x) for x in list(new_cell_par[0])])
    line_1 = '\t'.join([str(x) for x in list(new_cell_par[1])])
    line_2 = '\t'.join([str(x) for x in list(new_cell_par[2])])
    os.system('sed -i "3c ' + line_0 + '" POSCAR')
    os.system('sed -i "4c ' + line_1 + '" POSCAR')
    os.system('sed -i "5c ' + line_2 + '" POSCAR')


def converge_test(test_type, grad):
    try:
        os.mkdir(test_type)
    except FileExistsError:
        print(colour("Folder {} exits!".format(test_type)))
        sys.exit()
    os.chdir(test_type)
    tmp_wd = os.getcwd()
    for i in grad:
        new_i = ''.join(str(i).split())
        if new_i[0] == '-':
            new_i = 'o' + new_i
        os.system('mkdir ' + new_i)
        os.system('cp ../tmpl/* ' + new_i)
        os.chdir(new_i)
        if test_type == 'ENCUT':
            old_encut = os.popen('grep ENCUT INCAR | grep -P "\d+" -o').read().strip()
            os.system('sed -i "s/' + old_encut + '/' + new_i + '/g"  INCAR')
            os.popen('(echo 1; echo N)| python ~/scripts/bat_run.py').read()
            print('Job {} submitted.'.format(i))
        if test_type in ['SIGMA0', 'SIGMA1']:
            old_sigma = os.popen('grep SIGMA INCAR | grep -P "\d+\.\d*" -o').read().strip()
            os.system('sed -i "s/' + old_sigma + '/' + new_i + '/g"  INCAR')
            os.popen('(echo 1; echo N)| python ~/scripts/bat_run.py').read()
            print('Job {} submitted.'.format(i))
        if test_type == 'KPOINTS':
            os.system('sed -i "4c ' + i + '" KPOINTS')
            os.popen('(echo 1; echo N)| python ~/scripts/bat_run.py').read()
            print('Job {} submitted.'.format(i))
        if test_type == 'lattice':
            lattice(i)
            os.popen('(echo 1; echo N)| python ~/scripts/bat_run.py').read()
            print('Job {} submitted.'.format(i))
        os.chdir(tmp_wd)


converge_test(test, grad_dict[test])
