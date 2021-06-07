#!/bin/bash
while true;
END=30
do
for i in $(shuf -i 1-$END -n 1)
do 
result=`curl -s 192.168.49.2/api/fib/?x=$i`;
#dict=`curl -s localhost:5003/dict`;
echo $result
if [ "$result" == "None" ]; then
break
fi;
#echo $dict
#sleep 1
done
done