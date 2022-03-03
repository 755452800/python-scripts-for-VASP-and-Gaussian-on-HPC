import os
import time
import subprocess
import smtplib
from email.mime.text import MIMEText

"""
crontab 的环境变量需要自己设定的！
需要注意的是，/etc/profile中的环境变量无法调用conda中的python环境，需要额外设置 source /opt/software/anaconda3/env.sh;
"""


def send_mail(m):
    mail_host = "smtp.qq.com"
    mail_sender, mail_pass, mail_receiver = tuple(
        ['1099213337@qq.com', 'xxxxxxxxxxxxxx', 'xxxxxxxxx@xxxxxxx.edu.cn'])
    message_content = ''.join(m)
    message = MIMEText(message_content, 'plain', 'utf-8')
    message['Subject'] = 'NMI hpc notification'
    message['From'] = mail_sender
    message['To'] = mail_receiver
    try:
        # smtpObj = smtplib.SMTP()
        smtpobj = smtplib.SMTP_SSL(mail_host)
        smtpobj.login(mail_sender, mail_pass)
        smtpobj.sendmail(
            mail_sender, mail_receiver, message.as_string())
        print(time.ctime(time.time()))
        print(message_content)
        smtpobj.quit()
    except smtplib.SMTPException as e:
        print('error', e)


info = os.popen('pbsnodes | grep "     state"').readlines()
downnodes = []
for node in info:
    if node in ['     state = down\n', '     state = down,job-exclusive\n']:
        downnodes.append(info.index(node) + 1)

if len(downnodes) != 0:
    prompt1 = os.popen('date').read() + "Attention: Node {} down. Trying to restart down node(s)...\n".format(downnodes)
    print(prompt1)
    prompt = [prompt1]
    for node in downnodes:
        if node == 1:
            up_info = subprocess.Popen("{cmd}".format(cmd='service pbs_mom restart'), shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            up_info = subprocess.Popen("ssh -tt node0{} {cmd}".format(node, cmd='service pbs_mom restart'), shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success_info = up_info.stdout.read().decode('utf-8')
        failure_info = up_info.stderr.read().decode('utf-8')
        if 'OK' in success_info or '确定' in success_info:
            prompt2 = "Node {} restarted!\n\n".format(node)
            print(prompt2)
        elif not success_info:
            prompt2 = "Node {} failed to restart:\n".format(node) + failure_info + '\n'
            print(prompt2)
        else:
            prompt2 = 'Node {} failed to restart node due to unknown reason:\n'.format(node) + failure_info + '\n'
            print(prompt2)
        prompt.append(prompt2)
    send_mail(prompt)
