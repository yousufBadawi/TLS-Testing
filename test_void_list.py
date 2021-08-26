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


ls_cert = os.popen("ls certificates").readlines()

for i in range(len(ls_cert)):
    if os.path.getsize("certificates/" + ls_cert[i][:-1]) == 0:
        cert_id = ls_cert[i][11:-6]
        print("cert nb ", cert_id, " is void... downloading again")
        get_cert = os.system("certsh cert " + cert_id + " > certificates/certificate" + cert_id + ".json")
