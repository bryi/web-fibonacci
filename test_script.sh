#!/bin/bash
while true;
END=20
do
for i in $(shuf -i 1-$END -n 1)
do 
result=`curl -s 192.168.49.2/api/?x=$i`;
echo $result
if [ "$result" == "None" ]; then
break
fi;
sleep 1
done
done