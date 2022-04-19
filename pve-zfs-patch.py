#!/usr/bin/python3

import hashlib
import os, sys
import socket
import subprocess
import json
from datetime import date
import shutil
	 
fqdn = socket.getaddrinfo(socket.gethostname(), 0, flags=socket.AI_CANONNAME)[0][3]
email_user = "root@pam"
conf_file = sys.path[0]+'/'+'pve-patch.conf'

# Проверям параметры запуска
noemail = False
if len(sys.argv) > 2:
	sys.exit("Script has only one argument: -noemail, exit.")
elif len(sys.argv) == 2:
	if sys.argv[1] == "-noemail":
		print("------ No send email mode on. ------")
		noemail = True
	else:
		sys.exit("Script has only one argument: -noemail, exit.")

# Читаем конфигурационный файл	
def get_conf(file):
    if os.path.isfile(file):
        with open(file,'r') as conf_file:
            try:
                data = json.load(conf_file)
            except json.decoder.JSONDecodeError:
                sys.exit('Not valid json in file ' + file)
        conf_file.close()
        return(data['CONF'])
    else:
        sys.exit('Conf file ' + file + ' not found')

# Считаем md5	
def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

# Получаем email из PVE
def GetEmail(email_user):
	try:
		user_inf = subprocess.run(["pvesh", "get", "/access/users/" + email_user, "--output-format", "json"], capture_output=True, text=True)
	except FileNotFoundError:
		sys.exit("pvesh utility not found, this is PVE system?")
	if user_inf.stderr != "":
		sys.exit("pvesh err: " + user_inf.stderr)
	user_inf = json.loads(user_inf.stdout)
	return user_inf["email"]

# Отправляем email	
def SendMail(email: str, Subject: str, Body: str):
    body_str_encoded_to_byte = Body.encode()
    return_stat = subprocess.run(["mail", "-s", Subject, email], input=body_str_encoded_to_byte)
    #print(return_stat) 

email = GetEmail(email_user)

patches = get_conf(conf_file)

for file in patches:

	try:
		checksumm_current = md5sum(file['SYSFILE'])
	except FileNotFoundError:
		sys.exit("File " + file['SYSFILE'] +" not found, this is PVE system?")
    
	print("-------------------------------------")
	print("File: " + file['SYSFILE'])

	if checksumm_current in file['PATCHES']:
		print("Do patching...")
		today = date.today()
		print("Backup original " + file['SYSFILE'] +" file. New file name: " + file['SYSFILE'] + "." + today.strftime("%Y-%m-%d"))
		os.rename(file['SYSFILE'], file['SYSFILE'] + "."  + today.strftime("%Y-%m-%d"))
		print("Copy patch file.")
		shutil.copy(sys.path[0] + '/' + file['PATCHES'][checksumm_current], file['SYSFILE'])
		if not noemail:
			print("Sending email whith info to: " + email)
			SendMail(email, "Patch applyed on " + fqdn, "Patch applyed on " + fqdn + " Original " + file['SYSFILE'] +" file rename to: " + file['SYSFILE'] + today.strftime("%Y-%m-%d"))
		print("Patch " + file['SYSFILE'] + " applyed.")
	else:
		flag = False
		for md5, path in file['PATCHES'].items():
			if md5sum(sys.path[0] + '/' + path) == checksumm_current:
				print("Patch "+ path + " already applyed.")
				flag = True
				break
		if flag:
			continue
		if not noemail:
			print("Sending email whith error to: " + email)
			SendMail(email, "Patch ERROR on " + fqdn, "Patch can not bee applyed to current version " + file['SYSFILE'])
		print("Error: Patch can not bee applyed to current version " + file['SYSFILE'])
		
