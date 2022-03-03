#!/usr/bin/bash
source ~/.bashrc
#WORKDIR=$SLURM_SUBMIT_DIR
#SLURM_WALLTIME=100000
WORKDIR=`pwd`
cd $WORKDIR
#iter=`tail -n 1 OSZICAR | awk '{printf $1}'`
iter=`grep -a F= OSZICAR | wc -l`
cputime=`grep "Elapsed time" OUTCAR |  awk '{printf $4}' | sed 's/\..*//g'`
if [ -z $SLURM_WALLTIME ]; then SLURM_WALLTIME=100000; fi

if [ -z $cputime ]; then
    NSW=$iter
else
#    NSW=$(expr $SLURM_WALLTIME \* $iter / $cputime)
    let NSW=SLURM_WALLTIME\*iter/cputime
#    echo $NSW
fi
if [ $NSW -eq 1 ]; then
    NSW=2
elif [ $NSW -gt 2 ] && [ $NSW -le 200 ]; then
#    NSW=$(expr $NSW \* 85 / 100 )   #using 85% of walltime
    let NSW=NSW\*85/100
elif [ $NSW -gt 200 ]; then
    NSW=200
fi

if [ $iter -gt 1 ]; then
    sed -i "s/NSW.*/NSW = ${NSW}/g" INCAR
    sed -i "s/POTIM.*/POTIM = 0.5/" INCAR
    echo "INCAR modified to further optimize sturcture... "
    python ~/scripts/continue.py
    echo -e "New job id: \c"
    (echo 1; echo Y)| python ~/scripts/bat_run.py | grep "job id is:" | awk '{printf $12}'
    # " and ' is different in awk
    echo -e "\n"
fi
