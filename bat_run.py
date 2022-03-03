#!/share/apps/nmi_python/miniconda3/bin/python


from run import node_select, job_sub, ntfy_set
from funcs import backrun

SQ = node_select()
job_id, job_name = job_sub(SQ)
ntfy_set(job_id, job_name, SQ)
backrun()
exit()
