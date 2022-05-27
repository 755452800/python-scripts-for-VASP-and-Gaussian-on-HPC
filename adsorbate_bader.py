
import os
import sys
from colour import colour


def des_folders():
    exclude_folder = input("Specif exclude folders & files (using space to seperate):")
    exclude_folders = exclude_folder.split()
    run_folder = input("Specif folders to run (default all, using space to seperate):")
    run_folders = run_folder.split()
    if run_folder:
        folders = run_folders
    else:
        folders = os.listdir()
    return folders, exclude_folders


def make_result_folder(info, cwd):
    current_folder = cwd.split(r"/")[-1]
    result_folder = current_folder + info
    try:
        os.mkdir(result_folder)
    except FileExistsError:
        print(colour('Folder {} exists!'.format(result_folder)))
        sys.exit()
    return result_folder


def atom_number_of_adsorbate():
    atom_number_of_adsorbate = input("Input the atom number of adsorbate:\n")
    try:
        atom_number_of_adsorbate = int(atom_number_of_adsorbate)
        if atom_number_of_adsorbate < 0:
            raise ValueError
    except ValueError:
        print(colour("Wrong input! Input should be positive integer!"))
        sys.exit()
    return atom_number_of_adsorbate


def bader_folder(name, cwd):
    os.chdir(name)
    count = 0
    for i in os.listdir():
        if i in ["ACF.dat", "POSCAR", "POTCAR"]:
            count += 1
    os.chdir(cwd)
    if count == 3:
        return True
    else:
        return False


def find_adsorbate_number(folder, n):
    atom_str = os.popen('sed -n 6p POSCAR').readline().split()
    atom_num_str = os.popen('sed -n 7p POSCAR').readline().split()
    atom_num_int = list(map(int, atom_num_str))
    atom_num = sum(atom_num_int)
    if n > atom_num or n < 0:
        print(colour("Adsorbate number greater than total atom number! Wrong num input or wrong POSCAR!"))
        sys.exit()
    line_8 = os.popen('sed -n 8p POSCAR | cut -c 1').read().strip()
    if line_8 in ["D", "d"]:
        lines = os.popen("sed -n '9,{}p' POSCAR".format(9 + atom_num - 1)).readlines()
    elif line_8 in ["S", "s"]:
        lines = os.popen("sed -n '10,{}p' POSCAR".format(10 + atom_num - 1)).readlines()
    else:
        print(colour("Something wrong with POSCAR, please check"))
        sys.exit()
    z_coord = []
    for line in lines:
        z_coord.append(line.split()[2])
    z = list(map(float, z_coord))
    index_list = sorted(range(len(z)), key=lambda k: z[k], reverse=True)  # niubi!
    # index_to_adsorbate = list(map(lambda x: str(x + 1), index_list[:n]))
    index_to_adsorbate = index_list[:n]
    new_atom_str = []
    for i in atom_str:
        new_atom_str.append([i])
    atom_expand = list(map(lambda x, y: x * y, new_atom_str, atom_num_int))
    atom_expand = sum(atom_expand, [])  # https://blog.csdn.net/XX_123_1_RJ/article/details/80591107
    labelled_sequence = [str(i) for i in list(range(1, atom_num + 1))]
    for i in index_to_adsorbate:
        labelled_sequence[i] = str(i + 1) + "_adsorbate"
    labelled_info = list(map(lambda x, y: x + y, atom_expand, labelled_sequence))
    ZVAL = os.popen("grep ZVAL POTCAR").readlines()
    ZVAL_list = []
    for i in ZVAL:
        ZVAL_list.append(i.split()[5])
    new_ZVAL_list = []
    for i in ZVAL_list:
        new_ZVAL_list.append([i])
    ZVAL_expand = list(map(lambda x, y: x * y, new_ZVAL_list, atom_num_int))
    ZVAL_expand = sum(ZVAL_expand, [])
    ACF = os.popen("cat ACF.dat").readlines()
    new_ACF = []
    for i in ACF[0:2]:
        i = i.strip("\n")
        if "CHARGE" in i:
            i = i + "\tZVAL\tElement\n"
        if "-" in i:
            i = i + "------------------\n"
        new_ACF.append(i)
    for i in range(atom_num):
        new_ACF.append(ACF[i + 2].strip("\n") + "\t" + ZVAL_expand[i] + "\t" + labelled_info[i] + "\n")
    for i in range(atom_num + 2, atom_num + 6):
        new_ACF.append(ACF[i])
    with open("{}_ACF.dat".format(folder), "w+") as f:
        f.writelines(new_ACF)
    print("{}_ACF.dat in {} generated".format(folder, os.getcwd()))


def loop_folder():
    cwd = os.getcwd()
    print("Working directory is: {}".format(cwd))
    folders, exclude_folders = des_folders()
    N = atom_number_of_adsorbate()
    result_folder = make_result_folder("-bader", cwd)
    for folder in folders:
        if folder in exclude_folders:
            continue
        if os.path.isfile(folder):
            continue
        if not bader_folder(folder, cwd):
            continue
        os.chdir(folder)
        find_adsorbate_number(folder, N)
        os.system("cp {}_ACF.dat ../{}".format(folder, result_folder))
        os.chdir(cwd)


if __name__ == "__main__":
    loop_folder()
