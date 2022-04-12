from netmiko import ConnectHandler
from datetime import datetime
import json

now = datetime.now()
# Get the date for filename (the format is dd-mm-yyyy)
date = now.strftime("%d-%m-%Y")
# Get the date for time in log
dateLog = now.strftime("%d-%m-%Y %H:%M:%S")
# Open file IPRuckus.txt (change the file directory according to where the file is placed)
with open('./Files/IPRuckus.txt') as ListIP:
    # Loop all the IP in IPRuckus.txt
    for host in ListIP:
        # Remove \n in IP list
        host = host.replace('\n','')
        devices = {
            "device_type": "ruckus_fastiron",
            "host": host,
        }
        # Set IP for log if fail to connect
        hostIp = devices["host"]
        # set login to 0 if fail then it will keep loop to change user until the backup success and login=1
        login = 0
        # Open file user (change the file directory according to where the file is placed)
        with open('./Files/UserList.json') as data_file:
            data = json.load(data_file)
            # Loop all user in file UserList.json
            for users in data['users']:
                # Set variable username dan password according to UserList.json
                devices["username"] = str(users["username"])
                devices["password"] = str(users["password"])
                # Loop the connection 2 times if somehow the first connection failed
                # (I set it to 1 to make the log write connect from 1 not 0)
                connect_try = 1
                while connect_try != 3 :
                    try:
                        # Try to connect with SSH protocol, if fail change to telnet protocol
                        try:
                            net_connect = ConnectHandler(**devices)
                        except:
                            devices["device_type"] = "ruckus_fastiron_telnet"
                            net_connect = ConnectHandler(**devices)
                        net_connect.enable()
                        # get hostname
                        hostname = net_connect.find_prompt()[:-1]
                        # cut SSH@ or telnet@ at hostname
                        if devices["device_type"] == "ruckus_fastiron_telnet":
                            hostname = hostname.replace('telnet@', '')
                        elif devices["device_type"] == "ruckus_fastiron":
                            hostname = hostname.replace('SSH@', '')
                        # Remove the space from host name
                        hostname = hostname.replace(' ', '-')
                        # Command for sending the backup from ruckus switch (change <Server_IP> according to server that will be used for backup)
                        command = f"copy running-config tftp <Server_IP> {hostname}_{date}"

                        # if you want to save the file base on segment you can edit the command like this for example
                        # if devices["host"][0:9] in "192.168.10":
                        #     command = f"copy running-config tftp <Server_IP> /Segment10/{hostname}_{date}"
                        # elif devices["host"][0:9] in "192.168.20":
                        #     command = f"copy running-config tftp <Server_IP> /Segment20/{hostname}_{date}"
                        # else:
                        #     command = f"copy running-config tftp <Server_IP> /OtherSegment/{hostname}_{date}"

                        net_connect.send_command(command)
                        net_connect.disconnect()

                        # Open the log file and write the success backup
                        file_object = open('./Files/log.txt', 'a')
                        file_object.write(f'{dateLog} Backup Successfully for {hostIp}\n')
                        file_object.close()
                        break
                        # set connect try to exit the loop
                        connect_try = 3
                        login = 1
                    except Exception as e:
                        # Open the log file and write trying to connect
                        hostIp = hostIp.replace('{''}', '')
                        file_object = open('./Files/log.txt', 'a')
                        file_object.write(f'{dateLog} retry to connect {hostIp} ({connect_try}) \n' )
                        file_object.close()
                        connect_try += 1
                        # if fail then exit the loop to the next IP and write can't connect to this ip with explanantion
                        if connect_try == 3 :
                            file_object = open('./Files/log.txt', 'a')
                            file_object.write(f'{dateLog} can\'t connect {hostIp} because {e}\n' )
                            file_object.close()
                            break
                #If login success and backup done then exit the current user loop and change to the next IP
                if login == 1:
                    file_object = open('./Files/log.txt', 'a')
                    file_object.write(f'{dateLog} Backup Successfully for {hostIp}\n')
                    file_object.close()
                    break
