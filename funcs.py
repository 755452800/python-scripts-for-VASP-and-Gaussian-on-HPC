#!/share/apps/nmi_python/miniconda3/bin/python

"""
Author: steven
Date: Tue Dec 14 11:19:20 CST 2021
Last modified on : Mon Feb 21 19:14:09 CST 2022

1. pay attention to the usage of 'or' in python
2. python read/write functions should be paid more attention, especially a+ w+ r+
3. bugs on 46-49 need investigation
4. pay more attention to regex  https://regex101.com/
5. more about global variables and loops and breaks
6. pay attention to the use of sys.argv[0:] not sys.argv[1:]
7. to show the work directory of past jobs in slurm, try `sacct -j 188677 --format "jobid,jobname%20,workdir%70"`,
    see more in https://stackoverflow.com/questions/24586699/how-to-find-from-where-a-job-is-submitted-in-slurm
"""
import os
import re
import sys
import time
import smtplib
from colour import colour
from email.mime.text import MIMEText
from datetime import datetime


def compu_set():
    gga_bf = False
    ivdw = False
    try:
        with open("POSCAR", "r"), open("POTCAR", "r"):
            pass
    except FileNotFoundError:
        print(colour("POSCAR and/or POTCAR file not found."))
        sys.exit()
    try:
        with open("INCAR", "r") as incar:
            lines = incar.readlines()
            for line in lines:
                clean_line = "".join(line.split())
                if clean_line in ["GGA=BF"]:
                    gga_bf = True
                    break
                if clean_line in ["IVDW=11"]:
                    ivdw = True
        ibrion_line = os.popen("grep '^\s*IBRION' INCAR").read()
        npar_line = os.popen("grep '^\s*NPAR' INCAR").read()
        try:
            ibrion = int(re.findall(r"\d+", ibrion_line)[0].strip())
        except ValueError:
            ibrion = 5
        if ibrion == 5 and npar_line:
            print(colour("Doing freq calculation (IBRION = 5) with NPAR tag can cause unwanted stop. Check IBRION and "
                         "remove NPAR in INCAR!"))
            sys.exit()
    except FileNotFoundError:
        print(colour("INCAR file not found."))
        sys.exit()
    try:
        with open("KPOINTS", "r") as kp:
            lines = kp.readlines()
            kp_type = lines[2].strip()[0]
            kp_grid = "".join(lines[3].split())
            gam = kp_type in ["g", "G"] and kp_grid in ["111"]
        return gga_bf, gam, ivdw
    except FileNotFoundError:
        print(colour("KPOINTS file not found."))
        sys.exit()


def copy_script(q):
    compu_set()
    if q == "Q8":
        if os.path.exists("Q8-script"):
            print(colour("Q8-script already exists, using this existing script to submit job...", clr="yellow"))
        else:
            os.system("cp ~/scripts/Q8-script .")
    else:
        if os.path.exists("Q6-script"):
            print(colour("Q6-script already exists, using this existing script to submit job...", clr="yellow"))
        else:
            os.system("cp ~/scripts/Q6-script .")
    # if compu_set()[0] or compu_set()[2]:
    os.system("cp ~/scripts/vdw_kernel.bindat .")


def job_rename(q):
    script__name = q + "-script"
    # old_jobname = os.popen("grep {} {}".format("'#SBATCH -J'", script__name)).read().split()[-1]
    new_jobname = os.path.abspath(".").split(r"/")[-1]
    rename_tag = os.system("sed -i 's/#SBATCH -J.*/#SBATCH -J {}/' {}".format(new_jobname, script__name))
    if rename_tag != 0:
        print(colour("Error occured when changing job name in job script!"))
    set_info = compu_set()
    # f = open(script__name, "r+")
    # t = f.read()
    if set_info[0]:
        print("Attention: using " + colour("GGA=BF...", clr="green"))
    if compu_set()[1]:
        gam_tag = os.system("sed -i 's/vasp_std/vasp_gam/' {}".format(script__name))
        if gam_tag == 0:
            print("Using " + colour("vasp_gam", clr="green") + " to run gam single point job...")
        if gam_tag != 0:
            print(colour("Error occured when changing vasp_std to vasp_gam in job script!"))
    # t = t.replace(old_jobname, new_jobname)  # attention needed, easy to overflow
    # add = "#####################################################################\n"
    # t = t + add
    # f.seek(0)
    # f.write(t)
    # f.close()
    return script__name, new_jobname


def modify_incar(q):
    script = q + "-script"
    kpar_line = os.popen("grep '^\s*KPAR' INCAR").read()
    npar_line = os.popen("grep '^\s*NPAR' INCAR").read()
    cores = int(os.popen("grep '{}' {}".format("#SBATCH -n", script)).read().split()[-1])
    if cores >= 100 and kpar_line == "":
        print(colour("KPAR needs to be set if total cores are >= 100 for efficiency reason."))
        sys.exit()
    if kpar_line != "":
        kpar = int(re.findall(r"\d.*(?=\s)", kpar_line)[0].strip())
        print(colour("KPAR has been set to {}".format(kpar), clr="yellow"))
        cores = cores / kpar
    sqrt_cores = int(cores ** 0.5)
    NPAR = 4
    for i in range(int(sqrt_cores) + 1, 1, -1):
        if (cores % i) == 0:
            NPAR = i
            break
    if npar_line == "":
        os.system("sed -i '$a   NPAR = {0}' INCAR".format(NPAR))
        print(colour("Added NPAR = {0} at the end of INCAR".format(NPAR), clr="yellow"))
    else:
        os.system("sed -i 's/NPAR.*/NPAR = {0}/g' INCAR".format(NPAR))
        # os.system('sed -i "{0}c NPAR = {1}" INCAR'.format(npar_line, NPAR))
        print(colour("NAPR in INCAR has been changed to {} accordingly!".format(NPAR), clr="yellow", dis="u"))


def job_info(job_status_):
    if job_status_ == "R":
        print("Job status is: " + colour("runing...", clr="green"))
    elif job_status_ == "PD":
        print("Job status is: " + colour("pending, ", clr="yellow") + "double check it.")
    else:
        print("Something may be wrong, check the status:")
        os.system("squeue")


def backrun():
    pid = os.getpid()
    os.popen("kill -TSTP " + str(pid))
    os.popen("kill -CONT " + str(pid))
    # os.popen("disown -a")
    # os.system("kill -CONT " + str(pid))
    # os.popen("disown -h " + str(pid)).read()
    # a = os.popen("jobs -l").read().split()[1]
    # s = re.findall(r"[0-9]+", s)[0]
    # os.system("bg %" + s)


def job_end_check(jobid, job_name, q):
    time.sleep(2)
    tmp_cwd = os.getcwd()
    slurm_out_name = "slurm-" + jobid + ".out"
    while True:
        time.sleep(10)
        try:
            f = open(slurm_out_name, "rb")
        except FileNotFoundError:
            continue
        first_line = str(f.readline())[2:-3]
        lines = f.readlines()
        need_stop_info = os.popen("grep 'had an illegal value' {} | tail -n1".format(slurm_out_name)).readlines()
        if need_stop_info:
            need_stop_info = colour("ERROR: Job in this folder {} is abnormal (unreasonable initial structure), "
                                    "will be cancelled in seconds....".format(tmp_cwd))
            os.system("scancel {}".format(jobid))
            return need_stop_info + "\n" + need_stop_info[0]
        stop_info = os.popen("grep slurmstepd {} | tail -n1".format(slurm_out_name)).readlines()
        if stop_info:
            return tmp_cwd + "\n" + stop_info[0]
        try:
            last_line = lines[-1].decode("utf-8")
            # check_slurm_status = last_line.split(":")[0]
            # if check_slurm_status == "slurmstepd":
            #     return tmp_cwd + "\n" + last_line
        except IndexError:
            continue
        try:
            last_line_time = re.findall(
                r"\w{3}\s\w{3}\s{1,2}\d{1,2}\s\d{2}[:]\d{2}[:]\d{2}\s[CST]{3}\s\d{4}", last_line)[0]
        except IndexError:
            f.close()
            continue
        # f.seek(-2, os.SEEK_END)
        # first_line = f.readline()
        # while f.read(1) != b"":
        #     f.seek(-2, os.SEEK_CUR)
        # last_line = f.readline()
        f.close()
        end_time = datetime.strptime(last_line_time, "%a %b %d %H:%M:%S CST %Y")
        start_time = datetime.strptime(first_line, "%a %b %d %H:%M:%S CST %Y")
        # date_ = os.popen("echo `date`").read()[0:10]
        time_spent = (end_time - start_time).total_seconds() / 60
        if time_spent < 0.1:
            warning = colour("WARNING: ", clr="yellow") + "job {}({}) in folder {} finised instantly, check slurm " \
                                                          "output.".format(job_name, jobid, tmp_cwd)
            return warning
        issmear_status, sn = ismearcheck()
        if issmear_status:
            ismear_notify = ":hear-no-evil_monkey: \033[0;33;40mAttention:\033[0m entropy/atom_num = {:.4f} is " \
                            "greater than 0.001 eV, please check ISMEAR and SIGMA in INCAR file.\n\n".format(sn)
        else:
            ismear_notify = ""
        notification = "Starting from {}, job '{}'({}) ran on {} is now completed, time spent: {:.3f} min.\n\n{}". \
            format(start_time, job_name, jobid, q, time_spent, ismear_notify)
        end_lines_start_num = os.popen("grep -n F= " + slurm_out_name + " | tail -n1").read().split(":")[0]
        end_lines = "".join(os.popen("sed -n '" + end_lines_start_num + ",$p' " + slurm_out_name).readlines())
        if not end_lines:
            end_lines = os.popen("tail {}".format(slurm_out_name)).read()
        end_lines_from_vasp = "End lines from VASP:\n " + end_lines
        warnings_from_slurm = "Warnings from slurm output:\n" + "".join(
            os.popen("grep WARNING {}".format(slurm_out_name)).readlines()) + "\n"
        notification = notification + warnings_from_slurm + end_lines_from_vasp
        return notification


def mail_setting():
    configfile = "/share/home/shxhz1/scripts/mail_config.txt"
    try:
        fs = open(configfile, "rb")
        mail_serrings = fs.readlines()
        mail_sender = mail_serrings[0].split()[1]
        mail_passwd = mail_serrings[1].split()[1]
        mail_receiver = mail_serrings[2].split()[1]
        return mail_sender, mail_passwd, mail_receiver
    except FileNotFoundError:
        note = colour("Mail setting config not found, you may not receive notification.", clr="red")
        return note
    except IndexError:
        note = colour("Mail setting config not complete, you may not receive notification.", clr="red")
        return note


def send_mail(jobid, job_name, q):
    mail_host = "smtp.qq.com"
    mail_sender, mail_pass, mail_receiver = tuple(map(lambda byt: byt.decode("utf-8"), mail_setting()))
    message_content = job_end_check(jobid, job_name, q). \
        replace(":hear-no-evil_monkey:", "🙉").replace("[0;33;40m", "").replace("[0;32;40m", "").replace("[0m", "")
    message = MIMEText(message_content, "plain", "utf-8")
    message["Subject"] = "HPC notification"
    message["From"] = mail_sender
    message["To"] = mail_receiver
    try:
        # smtpObj = smtplib.SMTP()
        smtpobj = smtplib.SMTP_SSL(mail_host)
        smtpobj.login(mail_sender, mail_pass)
        smtpobj.sendmail(
            mail_sender, mail_receiver, message.as_string())
        smtpobj.quit()
        print(message_content.strip())
        print("Notification sent to {} successfully.\n".format(mail_receiver))
    except smtplib.SMTPException as e:
        print("error", e)


def ismearcheck():
    """
    For relaxations in metals use ISMEAR=1 or ISMEAR=2 and an appropriate SIGMA value (the entropy term should be less
    than 1 meV per atom). For metals a reasonable value is often SIGMA= 0.2 (which is the default, with ISMEAR being 1).
    ref: https://www.vasp.at/wiki/index.php/ISMEAR
         https://cms.mpi.univie.ac.at/vasp/vasp/ISMEAR_SIGMA_FERWE_FERDO_SMEARINGS_tag.html
    """
    ismear = os.popen("grep -n ISMEAR vasprun.xml | tail -n1").readline().split()[-1][0:1]
    if ismear in ["0", "1", "2"]:
        try:
            entropy = float(os.popen("grep 'entropy T' OUTCAR | tail -n1").readline().split()[-1])
        except IndexError:
            print(colour("NO OUTCAR file, check slurm output.", clr="red"))
            return False, 0
        atom_num_str = os.popen("sed -n 7p POSCAR").readline().split()
        try:
            atom_num = sum(list(map(int, atom_num_str)))
        except ValueError:
            atom_num_str = os.popen("sed -n 6p POSCAR").readline().split()  # incase the POSCAR is vasp4.x version
            atom_num = sum(list(map(int, atom_num_str)))
        flag = abs(entropy / atom_num)
        if flag > 0.001:
            return True, flag
        else:
            return False, flag
    else:
        return False, 0


def node_check():
    info = os.popen("sinfo").readlines()
    Q6 = 0
    Q8 = 0
    for line in info:
        node = line.split()
        if node[0] in ["Q6"] and node[4] == "idle":
            Q6 += 1
            continue
        if node[0] in ["Q8"] and node[4] == "idle":
            Q8 += 1
    if Q8 == 0 and Q6 != 0:
        return 1
    else:
        return 0
