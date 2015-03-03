#!/bin/bash
#mount backups first.
JB="/JenkinsBackups"
username=$1
password=$2
ip=$3
if [ ! -e $JB ]; then
	mkdir /JenkinsBackups
fi

if grep -qs $JB /proc/mounts; then
	umount -l $JB
fi
mount -t cifs -o username=$username,password=$password,domain=corp "//"$ip"/JenkinsShare" /JenkinsBackups

#copy the backups
for file in $(ls "/JenkinsBackups"  -t)
do
    if [ -d "/JenkinsBackups/"$file ];then
                if [[ ${file:0:4} == "FULL" ]];then
                        \cp -rf /JenkinsBackups/$file/* .
                        break
                fi
    fi
done
echo "restore is done..."


        
