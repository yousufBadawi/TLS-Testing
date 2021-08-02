domainList = ["protonirockerxow.onion"]

for i in range(0, len(domainList)):
    bashCommand = "torify openssl s_client -connect " + domainList[i] + ":443 -status"
    import subprocess

    process = subprocess.run(bashCommand.split(), input='q', encoding='ascii', capture_output=True)
    print(process.returncode)
    if process.returncode == 0:
        print("Process executed successfully")

    if process.stdout.find("no available protocols") != -1:
        print("Unsuccessful connection")

    print("Connection successful.")

    connection = process.stdout.split()

    highestSupportedVersion = "DNE"
    defaultCipher = ""
    for j in range(0, len(connection)):
        if connection[j].find("TLSv") != -1:
            print(connection[j])
            highestSupportedVersion = connection[j]
        if connection[j].find("Cipher") != -1:
            print(connection[j + 2])
            defaultCipher = connection[j+2]
            break

    # tls tests:
    tlsProtocols = ["-no_tls1_3", "-no_tls1_2", "-no_tls1_1"]
    tlsVersion = ["tls1.3", "tlsv1.2", "tlsv1.1"]
    tlsCommand = bashCommand
    lowestSupportedVersion = highestSupportedVersion
    failed = False
    for j in range(0, len(tlsProtocols)):
        tlsCommand += " " + tlsProtocols[j]
        print(tlsCommand)
        processTLS = subprocess.run(tlsCommand.split(), input='q', encoding='ascii', capture_output=True)
        print(processTLS.returncode)
        if processTLS.stdout.find("Cipher is (NONE)") != -1:
            print("Unsuccessful connection")
            failed = True
            break
    if j == 2 and not failed:
        print("Lowest supported version: SSL")
        lowestSupportedVersion = "SSL"
    else:
        print("Lowest supported version: " + tlsVersion[j])
        lowestSupportedVersion = tlsVersion[j]