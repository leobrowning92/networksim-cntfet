>alldata.csv
pattern=$1"*data.csv"
files=($pattern)
head ${files[0]} -n 1 >alldata.csv
cat $1*data.csv |grep -P "\d">>alldata.csv
