#!/bin/bash -xv
DATE=`date "+%Y-%m-%d %H:%M:%S"`
USER=$1
PASSWD=$2
echo "$USER:$PASSWD" | chpasswd
echo "$DATE change $USER's password successfully!"