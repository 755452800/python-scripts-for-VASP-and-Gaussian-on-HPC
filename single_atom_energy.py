#!/share/apps/nmi_python/miniconda3/bin/python

"""
Date: Thu Mar 11 11:02:57 CST 2021
Last modified: Fri Aug 13 15:44:06 CST 2021
@Author: steven
"""

import os
import sys
import shutil
import warnings
from colour import colour
from pymatgen.ext.matproj import MPRester
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

warnings.filterwarnings('ignore')
cwd = os.getcwd()
job_type = input('Select single atom type:\n1. bulk\n2. vacuum\n')
job_dict = {"1": 1, "": 1, "2": 2}
try:
    job = job_dict[job_type]
except KeyError:
    print(colour("Wrong input,try again"))
    sys.exit()
print("Current working directory is: {}".format(colour(cwd, clr='green')))
if os.path.exists('tmpl'):
    print('Template file folder is: {}'.format(colour('tmpl', clr='green')))
else:
    print(colour('No template file folder!'))
    sys.exit()
singleatoms = input('Sepcify input file:')
f = open(singleatoms, 'r')
elements = f.readlines()
f.close()


def bulk_single_atom(atom):
    os.chdir(atom)
    with MPRester() as mpr:
        material = mpr.get_data(atom)
        for item in material:
            if item['formation_energy_per_atom'] == 0.0:
                primitive_cell_struc = mpr.get_structure_by_material_id(item['material_id'])
                temp_struc = SpacegroupAnalyzer(primitive_cell_struc, symprec=0.01, angle_tolerance=5.0)
                conventional_cell_struc = temp_struc.get_conventional_standard_structure()
                conventional_cell_struc.to(fmt='poscar', filename='POSCAR')
    os.popen('(echo 103)|vaspkit').readlines()  # generate POTCAR file
    os.popen('(echo 102; echo 2; echo 0.03)|vaspkit').readlines()  # generate KPOINTS file
    tmpl_cwd = os.getcwd()
    shutil.copyfile(cwd + '/tmpl/INCAR', tmpl_cwd + '/INCAR')  # copy INCAR file to folder
    os.popen('(echo 1; echo N)| python ~/scripts/bat_run.py').read()  # submit vasp job


def vacuum_single_atom(atom):
    os.chdir(atom)
    tmpl_cwd = os.getcwd()
    shutil.copyfile(cwd + '/tmpl/POSCAR', tmpl_cwd + '/POSCAR')  # copy tmpl POSCAR file to folder
    os.system('sed -i "6c {}" POSCAR'.format(atom))  # generate POSCAR file
    os.popen('(echo 103)|vaspkit').readlines()  # generate POTCAR file
    os.popen('(echo 102; echo 2; echo 0.03)|vaspkit').readlines()  # generate KPOINTS file
    shutil.copyfile(cwd + '/tmpl/INCAR', tmpl_cwd + '/INCAR')  # copy INCAR file to folder
    os.popen('(echo 1; echo N)| python ~/scripts/bat_run.py').read()  # submit vasp job


for element in elements:
    element = element.strip('\n')
    if element == '':
        continue
    try:
        os.mkdir(element)
    except FileExistsError:
        print(colour("Folder {} exists! Skipping...".format(element)))
        continue
    if job == 1:
        bulk_single_atom(element)
    if job == 2:
        vacuum_single_atom(element)
    print(colour('Job "{}" assigned successfully.'.format(element), clr="green"))
    os.chdir(cwd)
