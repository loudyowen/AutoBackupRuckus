# AutoBackupRuckus
This script is for backing up Ruckus device automatically with multiple IP and multiple user, this script is using python and Netmiko.
For netmiko guide can be found here : https://github.com/ktbyers/netmiko
#How it works:
1. The script is using netmiko library for connecting the device
2. First it will open the Ruckus IP and loop all the IP in the file
3. Then it will loop the user in files/UserList.json to login to the first IP in the files/IPRuckus.txt
4. If the first user fail to connect the current IP then it will move the the next user in UserList.json
5. If the user logged in then it will run the command to run the backup, just like you use the command for backup manually
6. After that it will close the connection and write in the log.txt
