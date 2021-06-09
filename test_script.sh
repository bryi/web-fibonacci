#!/bin/bash
while true;
END=40
do
for i in $(shuf -i 1-$END -n 1)
do 
result=`curl -s http://api.bryidomain.tk/fib/?x=$i`;
#dict=`curl -s localhost:5003/dict`;
echo $result
if [ "$result" == "None" ]; then
break
fi;
#echo $dict
#sleep 3
done
done