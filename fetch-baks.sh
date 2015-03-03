#!/bin/bash
#mount backups first.
rootPath="/JenkinsBackups"
username=$1
password=$2
ip=$3
#where to backup
location=$4
if [ ! -e $rootPath ]; then
	mkdir /JenkinsBackups
fi

if grep -qs $rootPath /proc/mounts; then
	umount -l $rootPath
fi
mount -t cifs -o username=$username,password=$password,domain=corp "//"$ip"/JenkinsShare" /JenkinsBackups

#copy the backups
for file in $(ls "/JenkinsBackups/"$location  -t)
do
    if [ -d "/JenkinsBackups/"$file ];then
                if [[ ${file:0:4} == "FULL" ]];then
                        \cp -rf /JenkinsBackups/$file/* .
                        break
                fi
    fi
done
echo "restore is done..."


        
