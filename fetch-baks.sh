#!/bin/bash

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

mount -t cifs -o username=$username,password=$password,domain=corp "//"$ip"/JenkinsShare¡± /JenkinsBackups
