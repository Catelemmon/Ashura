#!/bin/bash -xv
DATE=`date "+%Y-%m-%d %H:%M:%S"`
USER=$1
PASSWD=$2
TAR_HOSTNAME=$3
echo "$DATE Verifying that the user ${USER} exists!"
cat /etc/passwd | awk -F ':' '{print $1}' | grep -m ${USER}>>/dev/null
if [[ $? != 0 ]];then
DATE=`date "+%Y-%m-%d %H:%M:%S"`
echo "$DATE adding user ${USER}!"
useradd ${USER} -m
echo "$DATE setting user ${USER}'s password!"
echo "$USER:$PASSWD" | chpasswd
DATE=`date "+%Y-%m-%d %H:%M:%S"`
echo "$DATE creating user public key pair!"
su ${USER}<<EOF
/usr/bin/expect
spawn ssh-keygen
expect "Enter file in which to save the key ($HOME/.ssh/id_rsa):"
send "\n"
expect "Enter passphrase (empty for no passphrase):"
send "\n"
expect "Enter same passphrase again:"
send "\n"
spawn ssh-copy-id $TAR_HOSTNAME
expect "$USER@TAR_HOSTNAME's password:"
send "$PASSWD\n"
interact
expect eof
exit
EOF
echo "$DATE add user: $USER successfully!"
make -C /var/yp
else
echo "$DATE the user $USER has been existed!"
fi