#!/share/apps/nmi_python/miniconda3/bin/python

import os
import sys
from colour import colour

cwd = os.getcwd()


def job_name():
    dir_name = os.path.abspath(".").split(r"/")[-1]
    return dir_name


def que_select():
    q_info = os.popen("qstat -q | grep -E -w 'core28|devlp|core48'").readlines()
    core28 = int(q_info[0].split()[5])
    devlp = int(q_info[1].split()[5])
    core48 = int(q_info[2].split()[5])
    print("core28: {}; devlp: {}; core48: {}".format(core28, devlp, core48))
    os.system("qstat -q | grep -E -w 'core28|devlp|core48'")
    if core48 < 2:
        return "core48"
    if core28 < 12:
        return "core28"
    if devlp == 0:
        return "devlp"
    else:
        return "core28"


def modify_script():
    q = que_select()
    ppn_dict = {"core28": "28", "devlp": "28", "core48": "48"}
    ppn = ppn_dict[q]
    name = job_name()
    copy_tag = os.system("cp ~/scripts/pbs.sub .")
    if copy_tag == 0:
        print(colour("<pbs.sub> copied to folder.", clr="green"))
    q_tag = os.system("sed -i 's/-q\s.*/-q {}/' pbs.sub".format(q))
    ppn_tag = os.system("sed -i 's/:ppn=.*/:ppn={}/' pbs.sub".format(ppn))
    np_tag = os.system("sed -i 's/-np\s\S*/-np {}/' pbs.sub".format(ppn))
    name_tag = os.system("sed -i 's/-N\s.*/-N {}/' pbs.sub".format(name))
    sub_tag = os.system("qsub pbs.sub")
    if q_tag == 0 and np_tag == 0 and ppn_tag == 0 and name_tag == 0 and sub_tag == 0:
        print(colour("Job {} submitted to {} successfully.".format(name, q), clr="green"))
    else:
        print(colour("Something wrong with <pbs.sub> script, please check."))
        sys.exit()


if __name__ == '__main__':
    modify_script()
