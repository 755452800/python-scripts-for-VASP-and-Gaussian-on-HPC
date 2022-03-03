#!/share/apps/nmi_python/miniconda3/bin/python

import os
import sys
import time
import emoji
import funcs
from colour import colour


def node_select():
    node_flag = funcs.node_check()
    if node_flag:
        Q = input("Specify Queue name:\n" + colour('1. Q6(default)', clr='green') + "\n2. Q8\n")
        Q_dict = {"": "Q6", "1": "Q6", "2": "Q8"}
    else:
        Q = input("Specify Queue name:\n" + colour('1. Q8(default)', clr='green') + "\n2. Q6\n")
        Q_dict = {"": "Q8", "1": "Q8", "2": "Q6"}
    try:
        Q = Q_dict[Q]
        return Q
    except KeyError:
        print(colour("Wrong input,try again"))
        sys.exit()


def job_sub(sq):
    funcs.copy_script(sq)
    script_name, jobname = funcs.job_rename(sq)
    funcs.modify_incar(sq)
    jobid = os.popen("sbatch " + script_name).read().split()[-1]
    time.sleep(1)
    squeue_info = os.popen("squeue").read().split()
    try:
        job_status = squeue_info[squeue_info.index(jobid) + 4]
    except ValueError:
        print("Job finished instantly, " + colour("ERROR") + " may have occured, check slurm output.")
        sys.exit()
    else:
        print("Job {} is now submitted to {}, slurm job id is: {}".
              format(colour(jobname, clr="cyan"), sq, colour(jobid, clr="green")))
        funcs.job_info(job_status)
    return jobid, jobname


def ntfy_set(jobid, jobname, sq):
    send = input("Send notification to mail when finished? (Y/N) (default Y)")
    send_dict = {"": "Y", "Y": "Y", "y": "Y", "n": "N", "N": "N"}
    if send_dict[send] == "Y":
        os.popen("nohup python -u ~/scripts/notification.py " + jobid + " " + jobname + " " + sq + ">>nohup.out "
                                                                                                "2>&1 &").read()
        note = funcs.mail_setting()
        flag = len(note)
        if flag == 3:
            print("Notification mail will be sent to {}!".format(note[2].decode()))
        else:
            print(note)


if __name__ == '__main__':
    SQ = node_select()
    job_id, job_name = job_sub(SQ)
    ntfy_set(job_id, job_name, SQ)
    funcs.backrun()
    prompt = funcs.job_end_check(job_id, job_name, SQ)
    print(emoji.emojize(prompt))
    exit()
