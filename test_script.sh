#!/bin/bash
while true;
END=40
do
for i in $(shuf -i 1-$END -n 1)
do 
result=`curl -s http://localhost:5000/fib/?x=$i`;
#dict=`curl -s localhost:5003/dict`;
echo $result
if [ "$result" == "None" ]; then
break
fi;
#echo $dict
sleep 1
done
done