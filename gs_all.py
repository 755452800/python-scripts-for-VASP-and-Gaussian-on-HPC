#!/share/apps/nmi_python/miniconda3/bin/python

import os
import sys
from colour import colour

cwd = os.getcwd()
print("Current working directory is: {}".format(cwd))
Generate_and_submit_choice = input("Specify options:\n1. cif/xsd file --> POSCAR\n2. POSCAR --> POTCAR\n3. POSCAR --> "
                                   "KPOINTS\n4. INCAR & cif/xsd --> submit all\n5. INCAR & POSCAR --> submit all\n6. "
                                   "submit jobs\n")
choice_dict = {"1": "gen_POSCAR", "2": "gen_POTCAR", "3": "gen_KPOINTS", "4": "1+2+3+6", "5": "2+3+6", "6": "sub_all"}
try:
    choice = choice_dict[Generate_and_submit_choice]
except KeyError:
    print(colour("Wrong input,try again"))
    sys.exit()
exclude_folder = input("Specif exclude folders & files (using space to seperate):")
exclude_folders = exclude_folder.split()
run_folder = input("Specif folders to run (default all, using space to seperate):")
run_folders = run_folder.split()
if run_folder:
    folders = run_folders
else:
    folders = os.listdir(cwd)


def gen_POSCAR(path):
    cif_flag = 0
    xsd_flag = 0
    for f in os.listdir():
        if f.endswith(".cif"):
            cif_flag += 1
            os.popen("(echo 105; echo " + f + "; echo -e '\n')|vaspkit").readlines()  # generate POSCAR file
            print('POSCAR in {} genereted.'.format(path))
        if f.endswith(".xsd"):
            xsd_flag += 1
            os.popen("(echo 106; echo " + f + ")|vaspkit").readlines()  # generate POSCAR file
            print("POSCAR in {} genereted.".format(path))
    if cif_flag == 0 and xsd_flag == 0:
        print(colour("No cif/xsd file in {}.".format(path)))
        sys.exit()
    if cif_flag > 1 or xsd_flag > 1:
        print(colour("Multiple cif/xsd file in {}!".format(path)))


def gen_POTCAR(path):
    if os.path.exists("POSCAR"):
        os.popen("(echo 103)|vaspkit").readlines()  # generate POTCAR
        print("POTCAR in {} genereted.".format(path))
    else:
        print(colour("No POSCAR file in {}".format(path)))


def gen_KPOINTS(path):
    if os.path.exists("POSCAR"):
        os.popen("(echo 102; echo 2; echo 0.03)|vaspkit").readlines()  # generate KPOINTS file
        print("KPOINTS in {} genereted using Gamma Scheme with a accuracy level of 0.03.".format(path))
    else:
        print(colour("No POSCAR file in {}".format(path)))


def sub_all(path):
    job_info = os.popen("(echo 1; echo Y)| python ~/scripts/bat_run.py").read()
    if "file not found" in job_info:
        print(colour("Job '{}' missing VASP input file(s)!".format(path)))
    else:
        print(colour("Job '{}' submitted successfully.".format(path), clr="green"))


for i in folders:
    if i in exclude_folders:
        continue
    try:
        os.chdir(i)
    except NotADirectoryError:
        continue
    if choice == "gen_POSCAR":
        gen_POSCAR(i)
    if choice == "gen_POTCAR":
        gen_POTCAR(i)
    if choice == "gen_KPOINTS":
        gen_KPOINTS(i)
    if choice == "1+2+3+6":
        gen_POSCAR(i)
        gen_POTCAR(i)
        gen_KPOINTS(i)
        sub_all(i)
    if choice == "2+3+6":
        gen_POTCAR(i)
        gen_KPOINTS(i)
        sub_all(i)
    if choice == "sub_all":
        sub_all(i)
    os.chdir(cwd)
