#!/share/apps/nmi_python/miniconda3/bin/python

import sys
import funcs

# parameters = sys.argv[0:]
parameters = sys.argv
funcs.send_mail(parameters[1], parameters[2], parameters[3])
exit()
