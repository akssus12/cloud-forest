#!/bin/bash
ps -elf | grep kakao_chatbot.py | awk '{print $4}' > temp.txt

cat temp.txt | while read line || [[ -n "$line" ]];
do
        kill -9 $line
done

nohup python3 -u kakao_chatbot.py &

