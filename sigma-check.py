import os
from colour import colour


def ismearcheck():
    tmp_cwd = os.getcwd()
    if not os.path.exists('vasprun.xml'):
        print(colour('NO vasprun.xml in folder: {}'.format(tmp_cwd), clr="yellow"))
        return False, 0
    ismear = os.popen('grep -n ISMEAR vasprun.xml | tail -n1').readline().split()[-1][0:1]
    if ismear in ['0', '1', '2']:
        try:
            entropy = float(os.popen('grep "entropy T" OUTCAR | tail -n1').readline().split()[-1])
        except IndexError:
            print(colour('NO OUTCAR file, check slurm output. Folder: {}'.format(tmp_cwd), clr="yellow"))
            return False, 0
        atom_num_str = os.popen("sed -n 7p POSCAR").readline().split()
        try:
            atom_num = sum(list(map(int, atom_num_str)))
        except ValueError:
            atom_num_str = os.popen("sed -n 6p POSCAR").readline().split()
            atom_num = sum(list(map(int, atom_num_str)))
        result = abs(entropy / atom_num)
        if result > 0.001:
            return True, result
        else:
            print(colour('entropy/atom_num = {:.4f} is smaller than 0.001 eV in folder {}'.format(result, tmp_cwd),
                         clr="green"))
            return False, result
    else:
        print(colour('ISMEAR is not set to [0,1,2] in folder: {}'.format(tmp_cwd), clr="green"))
        return False, 0


def work(path):
    flag, result = ismearcheck()
    if not flag:
        os.chdir(cwd)
    else:
        print(colour('entropy/atom_num = {:.4f} is greater than 0.001 eV in folder {}'.format(result, path),
                     clr="red"))
        os.chdir(cwd)


cwd = os.getcwd()
print('Current working directory is: {}'.format(cwd))
exclude_folder = input('Specif exclude folders & files (using space to seperate):')
exclude_folders = exclude_folder.split()
work(cwd)

for i in os.listdir(cwd):
    if i in exclude_folders:
        continue
    try:
        os.chdir(i)
    except NotADirectoryError:
        continue
    tmp_cwd = os.getcwd()
    work(tmp_cwd)
