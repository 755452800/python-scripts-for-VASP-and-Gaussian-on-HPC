#!/share/apps/nmi_python/miniconda3/bin/python


import os
from colour import colour

init_cwd = os.getcwd()
print(colour("Current working directory: {}".format(init_cwd), clr="green"))
exclude_folder = input("Specif exclude folders & files (using space to seperate):")
exclude_folders = exclude_folder.split()
all_thermo_info = []


def vasp_folder(name):
    os.chdir(name)
    count = 0
    for i in os.listdir():
        if i in ["INCAR", "POSCAR", "POTCAR", "KPOINTS", "CONTCAR", "OUTCAR"]:
            count += 1
    os.chdir(init_cwd)
    if count >= 5:
        return True


for i in os.listdir("."):
    if i in exclude_folders:
        continue
    if os.path.isfile(i):
        continue
    if not vasp_folder(i):
        continue
    os.chdir(i)
    thermo_info = os.popen("(echo 501; echo 298.15)|vaspkit | grep -A 6 'Temperature (T)'").readlines()
    zpe_id = thermo_info[1].split(":")[0].strip().split()[-1]
    zpe_value = thermo_info[1].split(":")[-1].split()[-2]
    Ut_id = thermo_info[2].split(":")[0].strip().split()[-1]
    Ut_value = thermo_info[2].split(":")[-1].split()[-2]
    Ht_id = thermo_info[3].split(":")[0].strip().split()[-1]
    Ht_value = thermo_info[3].split(":")[-1].split()[-2]
    Gt_id = thermo_info[4].split(":")[0].strip().split()[-1]
    Gt_value = thermo_info[4].split(":")[-1].split()[-2]
    S_id = thermo_info[5].split(":")[0].strip().split()[-1]
    S_value = thermo_info[5].split(":")[-1].split()[-2]
    TS_id = thermo_info[6].split(":")[0].strip().split()[-1]
    TS_value = thermo_info[6].split(":")[-1].split()[-2]
    all_thermo_info.append(
        [i, zpe_id, zpe_value, Ut_id, Ut_value, Ht_id, Ht_value, Gt_id, Gt_value, S_id, S_value, TS_id, TS_value])
    os.chdir(init_cwd)

os.chdir(init_cwd)
f = open("thermo-correction-results.txt", "a+")
prompt_info = '\n' + os.popen("date").read()
f.write(prompt_info)
for info in all_thermo_info:
    print(info)
    f.write(str(info))
    f.write("\n")
f.close()
print("Done! Thermo-correction results wrote to:\n\t" + colour("thermo-correction-results.txt", clr="green"))
