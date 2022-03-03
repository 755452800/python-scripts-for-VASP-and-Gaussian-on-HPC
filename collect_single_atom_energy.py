#!/share/apps/nmi_python/miniconda3/bin/python

"""
Date: Fri Mar 12 15:49:36 CST 2021
Last modified: Fri Aug 13 17:00:27 CST 2021
@Author: steven
a fucking tip: os.walk(path) path should not just be '.'
pay attention to if or!
"""

import os
from colour import colour

single_atom_energy = []
init_cwd = os.getcwd()
print(colour('Current working directory: {}'.format(init_cwd), clr="green"))

for roots, dirs, files in os.walk(init_cwd):
    for folder in dirs:
        temp_cwd = os.path.join(roots, folder)
        os.chdir(temp_cwd)
        info = os.popen('qvasp -e').readlines()
        energy = info[1][51:-5]
        if energy in ['onvergen', 'eck it', '']:
            continue
        status = info[2][29:-7]
        try:
            f1 = open("POSCAR", 'r')
        except FileNotFoundError:
            print(colour("{} folder has no POSCAR file, skpping...".format(temp_cwd), clr="yellow"))
            continue
        pos = f1.readlines()
        atom = pos[5].strip()
        number = pos[6].strip()
        energy_per_atom = float(energy) / int(number)
        single_atom_energy.append([temp_cwd, atom, float(energy), int(number), energy_per_atom, status])


def energy_sum():
    os.chdir(init_cwd)
    f = open("energy-results.txt", 'a+')
    prompt_info = '\n' + os.popen('date').read()
    f.write(prompt_info)
    for line in single_atom_energy:
        print(line)
        f.write(str(line))
        f.write('\n')
    f.close()
    print('Done! Energy results wrote to:\n\t' + colour('energy-results.txt', clr="green"))


energy_sum()
