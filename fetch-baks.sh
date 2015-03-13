#!/bin/bash
#mount backups first.
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
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
#        umount -l $rootPath
         echo "no need to mount"
else
         mount -t cifs -o username=$username,password=$password,domain=corp "//"$ip"/JenkinsShare" /JenkinsBackups
fi

#copy the backups
for file in $(ls "/JenkinsBackups/"$location  -t)
do
    backupLocation="/JenkinsBackups/"$location/$file
    if [ -d $backupLocation ];then
                if [[ ${file:0:4} == "FULL" ]];then
                        echo $file
                        for f in $(ls $backupLocation)
                        do
                            \cp -rf "$backupLocation/$f" .
                        done
                        #\cp -rf $backupLocation/* .
                        break
                fi
    fi
done
echo "restore is done..."
IFS=$SAVEIFS
