#!/share/apps/nmi_python/miniconda3/bin/python

import os
import sys
from colour import colour


def make_dir(name):
    try:
        os.mkdir(name)
        return True
    except FileExistsError:
        print(colour("{} exists, skipping...".format(name)))
        return False


def vasp_folder(name):
    os.chdir(name)
    count = 0
    for i in os.listdir():
        if i in ["INCAR", "POSCAR", "POTCAR", "KPOINTS", "CONTCAR", "OUTCAR"]:
            count += 1
    os.chdir(cwd)
    if count >= 5:
        return True


def con2pos(name):
    os.chdir(name)
    # ways to modify INCAR
    # os.system("sed -i '/\<EDIFF\>/c EDIFF = 1E-7' INCAR")
    os.system("sed -i 's/EDIFF[^G].*/EDIFF = 1E-7/' INCAR")
    os.system("sed -i 's/^\s*NPAR/#NPAR/' INCAR")
    # os.system("sed -i '/\<IBRION\>/c  IBRION = 5' INCAR")
    os.system("sed -i 's/IBRION.*/IBRION = 5/' INCAR")
    # os.system("sed -i '/\<POTIM\>/c  POTIM = 0.015' INCAR")
    os.system("sed -i 's/POTIM.*/POTIM = 0.015/' INCAR")
    # os.system("sed -i '/\<POTIM\>/aNFREE = 2' INCAR")
    os.system("sed -i '/POTIM/a\   NFREE = 2' INCAR")
    os.system("cp CONTCAR POSCAR")
    print("CONTCAR in {} copied to POSCAR".format(name))
    os.system("rm slurm*")
    relax_top_atoms(relax_atom_num)
    os.chdir(cwd)


def relax_top_atoms(num):
    os.popen(
        "(echo 402; echo 1; echo 2; echo 0 0; echo 2;)|vaspkit").readlines()  # generate POSCAR_FIX with Cartesian coord
    atom_num_str = os.popen('sed -n 7p POSCAR_FIX | tail -n1').readline().split()
    atom_num = sum(list(map(int, atom_num_str)))
    if num > atom_num:
        print(colour("Relax atom number greater than total atom number! Wrong num input or wrong POSCAR/CONTCAR!"))
        sys.exit()
    os.system("sed -i 's/T  T  T/F  F  F/g' POSCAR_FIX")
    lines = os.popen("sed -n '10,$p' POSCAR_FIX").readlines()
    z_coord = []
    for line in lines:
        z_coord.append(line.split()[2])
    z = list(map(float, z_coord))
    index_list = sorted(range(len(z)), key=lambda k: z[k], reverse=True)  # niubi!
    index_to_relax = index_list[:num]
    for i in index_to_relax:
        z_relax = z_coord[i]
        os.system("sed -i 's/{}    F  F  F/{}    T  T  T/g' POSCAR_FIX".format(z_relax, z_relax))
    os.system("cp POSCAR_FIX POSCAR")
    print("Selected top atoms set relaxed.")


cwd = os.getcwd()
exclude_folder = input("Specif exclude folders & files (using space to seperate):")
exclude_folders = exclude_folder.split()
run_folder = input("Specif folders to run (default all, using space to seperate):")
run_folders = run_folder.split()
# if os.path.exists('tmpl'):
#     print('Template file folder is: {}'.format(colour('tmpl', clr='green')))
# else:
#     print(colour('No template file folder <tmpl>!'))
#     sys.exit()
top_atoms = input("How many atoms to be set to relaxed on top?\n")
try:
    relax_atom_num = int(top_atoms)
    if relax_atom_num < 0:
        raise ValueError
except ValueError:
    print(colour("Wrong input! Input should be positive integer!"))
    sys.exit()
if run_folder:
    folders = run_folders
else:
    folders = os.listdir()
try:
    os.mkdir("freq")
except FileExistsError:
    print(colour("Attention: folder <freq> exists!", clr="yellow"))
for folder in folders:
    if folder in exclude_folders:
        continue
    if os.path.isfile(folder):
        continue
    if not vasp_folder(folder):
        continue
    if folder.split("_")[-1] == "freq":
        continue
    freq_name = folder + "_freq"
    freq_name = "freq/" + freq_name
    flag = make_dir(freq_name)
    if not flag:
        continue
    os.system("cp -r {}/* {}/".format(folder, freq_name))
    if os.popen("grep '^\s*NPAR' {}/INCAR".format(freq_name)).read():
        print(colour("NPAR tag should be removed for most freq calculations! Will comment out NPAR...", clr="yellow"))
    con2pos(freq_name)
print(colour("Remeber to check if atoms are fixed/relaxed properly in POSCAR before freq calculation!", clr="yellow"))
