import os
import json


def create_if_not_here(directory, path=""):  #path without final backlash 
    ls_directory = os.popen("ls " + path).readlines()
    cert_already_created = False
    for i in range(len(ls_directory)):
        dir = str(directory) + "\n"
        if ls_directory[i] == dir:
            cert_already_created = True
    if cert_already_created == False:
        if path == "":
            creation = os.system("mkdir " + str(directory))
        else:
            creation = os.system("mkdir " + str(path) + "/" + str(directory))

def cert_exist(file):
    ls_certificates = os.popen("ls " + "certificates").readlines()
    cert_already_exist = False
    for i in range(len(ls_certificates)):
        cert = str(file) + "\n"
        if ls_certificates[i] == cert:
            cert_already_exist = True
    return cert_already_exist
    


get_onion_sites =  os.system("certsh domain .onion > onion_sites.txt")

create_if_not_here("certificates")


f = open("onion_sites.txt", "r")
lines = f.readlines()
k=0
for line in lines:
    crtsh_id = line.split()[0]
    if(not(cert_exist("certificate" + crtsh_id + ".json"))):    
        get_cert = os.system("certsh cert " + crtsh_id + " > certificates/certificate" + crtsh_id + ".json")    
    print(k+1, "/", len(lines))
    k+=1

f.close()