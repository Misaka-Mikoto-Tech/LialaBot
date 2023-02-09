#!/bin/sh
cd /docker-data/haruka-bot
nohup hb run &
sleep 5

cd /docker-data/go-cqhttp_3175613658_YiCheng-Bot
nohup go-cqhttp &
sleep 5

cd /docker-data/go-cqhttp_372135609_Misaka
nohup go-cqhttp &
sleep 5

cd /docker-data/go-cqhttp_2523741995_Liala-Bot
nohup go-cqhttp &
sleep 5



echo
echo type [quit] if you want quit
read USER_INPUT
while [ "$USER_INPUT" != "quit" ];do
	read USER_INPUT
done