import os
import sys
import time


def node_status():
    info = os.popen('sinfo').readlines()
    Q6 = 0
    # Q7 = 0
    Q8 = 0
    for line in info:
        node = line.split()
        if node[0] in ['Q6'] and node[4] == 'idle':
            Q6 += 1
            continue
        # if node[0] in ['Q7'] and node[4] == 'idle':
        #     Q7 += 1
        #     continue
        if node[0] in ['Q8'] and node[4] == 'idle':
            Q8 += 1
    return Q6, Q8


def job_status():
    pd_job_info = {}
    info = os.popen('squeue --format "%i %t %Z"').readlines()
    for line in info:
        if line.split()[1] == 'PD':
            pd_job_info[line.split()[0]] = line.split()[-1]
    return pd_job_info


PD_JOB_INFO = job_status()
if len(PD_JOB_INFO) == 0:
    sys.exit()
for job_id, job_path in PD_JOB_INFO.items():
    NODE_Q6, NODE_Q8 = node_status()
    if NODE_Q6 == 0 and NODE_Q8 == 0:
        sys.exit()
    print(os.popen('date').read().strip())
    print('{} idle left in Q6'.format(NODE_Q6))
    print('{} idle left in Q8'.format(NODE_Q8))
    os.popen('scancel {}'.format(job_id))
    print('Job {} in {} cancelled'.format(job_id, job_path))
    os.chdir(job_path)
    job_info = os.popen('(echo 1; echo Y)| python ~/scripts/bat_run.py').read()
    print('Job {} in {} changed to another partition\n'.format(job_id, job_path))
    time.sleep(10)
