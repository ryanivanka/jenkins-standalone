#!/bin/bash
#---------Initialize arguments---------
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
rootPath="JenkinsBackups"
sourcePath="JenkinsShare"

while [[ $# > 1 ]]; do
    key="$1"
    shift
    case $key in
        -lc|--location)
            location="$1"
            echo "Get required location=$1"
            shift
            ;;
        -ip|--ip-address)
            ip="$1"
            echo "Get ip=$1"
            shift
            ;;
        -u|--username)
            username="$1"
            echo "Get username=$1"
            shift
            ;;
        -p|--password)
            password="$1"
            echo "Get password"
            shift
            ;;
        -src|--sourcePath)
            sourcePath="$1"
            echo "Get sourcePath=$1"
            shift
            ;;
        -h|--home)
            rootPath="$1"
            echo "Get rootPath=$1"
            shift
            ;;
        *)
            echo "Unknown option: ${key}"
            exit 1
            ;;
    esac
done


#---------mount Jenkinsbackup folder from sharefolder--------
if [[ ! -d "/$rootPath" ]]; then
        echo "make rootPath directory"
        mkdir /"$rootPath"
fi

echo "fetch backup"
if grep -qs "/$rootPath" /proc/mounts; then
         echo "no need to mount..."
elif [[ -z "$ip" ]]; then
        echo "mount JenkinsBackups from default machine: docker-registry1:/$sourcePath /$rootPath"
        mount docker-registry1:/"$sourcePath" /"$rootPath"
        echo "mount success"
else
        echo "mount JenkinsBackups from ip user provide: mount -t cifs -o username=$username,domain=corp $ip/$sourcePath /$rootPath"
        mount -t cifs -o username="$username",password="$password",domain=corp //"$ip"/"$sourcePath" /"$rootPath"
        echo "mount success"
fi


#---------restore the backups------
echo "start restore /$rootPath/$location/Full*/* ."
cp -rf /"$rootPath"/"$location"/FULL*/* .
echo "restore success"

IFS=$SAVEIFS
