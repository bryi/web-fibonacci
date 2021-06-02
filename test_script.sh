#!/bin/bash
while true;
END=10 
do
for i in $(shuf -i 1-$END -n 1); 
do 
result=`curl -s localhost:5000/?x=$i`;
echo $result;
dict=`curl -s localhost:5000/dict`;
echo $dict;
sleep 1 
done
done