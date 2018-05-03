#! /bin/bash

### All the subroutines are right here at the beginning ###

usage()
{
 cat <<EOF

   subpy - Leo's submission script pared down from Mathhias' script to handle only bash script submission.

 Syntax:
  subpy [-t <time>] [-P <cpunr>] [-m <memory>] [-d <disk>] [-n <node>] <filename.sh>

     <time> Job time in hh:mm:ss (Default $time).
    <cpunr> Request a parallel job running on <cpunr> CPUs (Default $cpunr).

   <memory> Requests ram in mb per processor (no suffix, Default $mem).
     <disk> Requests diskspace per processor (mb, gb or tb suffix, Default $disk).
     <node> Requests a specific node for the job.

   limitations: 1) You have to be in the same directory as your input file
                   when submitting the job.
                2) The names of input files have to end in ".sh"
EOF
exit 0
}

set_defaults()
{
# set defaults for the queueing system
time="24:00:00"
cpunr="1"
nodes="1"
mem="1024"
disk="10gb"
}


### The main part of the script starts here ###

# if no command line arguments are given, print usage information
set_defaults
[ -z "$1" ] && usage

# analyse command line arguments
while [ -n "$1" ]
do
   case $1 in
       -t) time=$2;shift;shift;;
       -P) cpunr="$2";shift;shift;;
       -m) mem="$2";shift;shift;;
       -d) disk="$2";shift;shift;;
       -n) nodes="$2";shift;shift;;
        *) jobname=$1;shift;;
   esac
done




# Removing the trailing ".sh" from $jobname
jobname=`echo $jobname | sed s/"\.sh$"/""/`

# chop the jobname to 15 characters max (PBS is so stupid!)
pbsname=${jobname:0:15}
# remove whitespace from names so the temp-files are not confused
pbsname=`echo $pbsname | sed s/" "/""/g`
stdname=$pbsname.`date +%a-%d-%b-%Y_%H-%M-%S`

# create the batch submitfile
submitfile=`mktemp $pbsname.XXXX`

# print out what is being submitted
echo "Requesting $time time on $cpunr cores across $nodes nodes. Running \"$jobname\" with $mem mb of memory."

################# generate header for job ###########################
cat > "$submitfile" <<EOF
#!/bin/bash
#Header for Slurm following
#SBATCH --job-name=$jobname
#SBATCH --output=$stdname.stdout
#SBATCH --error=$stdname.stderr
#SBATCH --nodes=$nodes
#SBATCH --ntasks=$cpunr
#SBATCH --time=$time
#SBATCH --mem-per-cpu=$mem
#SBATCH --workdir=$PWD
#SBATCH --kill-on-invalid-dep=yes
#SBATCH --mail-type=END
#SBATCH --mail-user=$USER@localhost
date
echo "User executing this job: \$SLURM_JOB_USER"
echo -n "We are on: " && hostname
echo ""

echo "The memory situation, as reported by free -m"
free -m
echo ""

echo -n "Number of processor cores on this node: " && nproc
echo ""


echo "---- The Job is executed NOW ----"
date

echo "---- The Job has finished NOW ----"
echo ""
date

echo "The memory situation, as reported by free -m"
free -m
echo ""
EOF

##### Specifics for running a general purpose script ############

cat >> "$submitfile" << EOF
#---- begin generic script part ----

cd $PWD
bash $PWD/$jobname.sh

#---- end generic script part ----

EOF

#################################################################

################# general footer for all jobs ###################
cat >> "$submitfile" << EOF

echo "---- The Job has finished NOW ----"
echo ""

date

echo "The memory situation, as reported by free -m"
free -m
echo ""

EOF

mv $submitfile $jobname.sub

sbatch "$jobname.sub" > $stdname.log
