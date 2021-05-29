import hashlib
import os, sys
import socket
import subprocess
import json
from datetime import date
import shutil

#------python 3.8+ version--------
#def md5sum(filename):
#     with open(os.path.abspath(filename), "rb") as f:
#         file_hash = hashlib.md5()
#         while chunk := f.read(8192):
#             file_hash.update(chunk)
#     return file_hash.hexdigest()
#---------------------------------
	 
fqdn = socket.getaddrinfo(socket.gethostname(), 0, flags=socket.AI_CANONNAME)[0][3]
email_user = "root@pam"

noemail = False
if len(sys.argv) > 2:
	sys.exit("Script has only one argument: -noemail, exit.")
elif len(sys.argv) == 2:
	if sys.argv[1] == "-noemail":
		print("------ No send email mode on. ------")
		noemail = True
	else:
		sys.exit("Script has only one argument: -noemail, exit.")
	
	
def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()
	
def SendMail(email: str, Subject: str, Body: str):
    body_str_encoded_to_byte = Body.encode()
    return_stat = subprocess.run(["mail", "-s", Subject, email], input=body_str_encoded_to_byte)
    print(return_stat) 

try:
	checksumm_origin = md5sum(sys.path[0] + '/' + "ZFSPoolPlugin.pm.orig")
except FileNotFoundError:
	sys.exit("File ZFSPoolPlugin.pm.orig not found, your need copy all files.")

try:
	checksumm_patch = md5sum(sys.path[0] + '/' + "ZFSPoolPlugin.pm.patch")
except FileNotFoundError:
	sys.exit("File ZFSPoolPlugin.pm.patch not found, your need copy all files.")

try:
	checksumm_current = md5sum("/usr/share/perl5/PVE/Storage/ZFSPoolPlugin.pm")
except FileNotFoundError:
	sys.exit("File ZFSPoolPlugin.pm not found, this is PVE system?")


try:
	user_inf = subprocess.run(["pvesh", "get", "/access/users/" + email_user, "--output-format", "json"], capture_output=True, text=True)
except FileNotFoundError:
	sys.exit("pvesh utility not found, this is PVE system?")
if user_inf.stderr != "":
	sys.exit("pvesh err: " + user_inf.stderr)

user_inf = json.loads(user_inf.stdout)
email = user_inf["email"]

print("checksumm original file:           " + checksumm_origin)
print("checksumm current file in system:  " + checksumm_current)
print("checksumm patch file:              " + checksumm_patch)
print("------------------------------------------")
if checksumm_current == checksumm_patch:
	sys.exit("Patch already applyed. Exit.")
else:
	if checksumm_current == checksumm_origin:
		print("Do patching...")
		today = date.today()
		print("Backup original ZFSPoolPlugin.pm file. New file name: ZFSPoolPlugin.pm." + today.strftime("%Y-%m-%d"))
		os.rename('/usr/share/perl5/PVE/Storage/ZFSPoolPlugin.pm', '/usr/share/perl5/PVE/Storage/ZFSPoolPlugin.pm.' + today.strftime("%Y-%m-%d"))
		print("Copy patch file.")
		#cp $(dirname "$0")/ZFSPoolPlugin.pm.patch /usr/share/perl5/PVE/Storage/ZFSPoolPlugin.pm
		shutil.copy(sys.path[0] + '/' + "ZFSPoolPlugin.pm.patch", "/usr/share/perl5/PVE/Storage/ZFSPoolPlugin.pm")
		if not noemail:
			print("Sending email whith info to: " + email)
			SendMail(email, "ZFS Encryption patch applyed on " + fqdn, "Patch applyed on " + fqdn + " Original ZFSPoolPlugin.pm file rename to: ZFSPoolPlugin.pm." + today.strftime("%Y-%m-%d"))
		sys.exit("Patch applyed. Exit.")
	else:
		if not noemail:
			print("Sending email whith info to: " + email)
			SendMail(email, "ZFS Encryption patch ERROR on " + fqdn, "Patch can not bee applyed to current version ZFSPoolPlugin.pm")
		sys.exit("Patch can not bee applyed to current version ZFSPoolPlugin.pm. Exit.")
		



