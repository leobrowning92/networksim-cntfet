>alldata.csv
pattern="data/*data.csv"
files=($pattern)
head ${files[0]} -n 1 >alldata.csv
cat data/*data.csv |grep -P "\d">>alldata.csv

